import json
import logging
import os
import sys
import threading
import csv

from tagger.daemon import daemon
from tagger.my_requests import Session
from tagger.ui import UI
from tagger.url_tree import XNATUrl


class App:
    def __init__(self, n_buffer, tag_options_file, input_filename, output_file, xnat_url, xnat_project, xnat_user,
                 xnat_pass=""):
        logging.basicConfig()
        self.logger = logging.getLogger("app")
        self.logger.setLevel("DEBUG")

        self.logger.info("Initializing app")
        with open(tag_options_file) as f:
            self.options = json.load(f)
        self.logger.debug(f"Tagging options: {self.options}")
        self.ui = UI(self.options, self)

        self.output_filename_lock = f'{os.path.dirname(output_file)}/.{os.path.basename(output_file)}.lock'
        if os.path.exists(self.output_filename_lock):
            print(f'Lock file exists in {self.output_filename_lock}. This usually means the program crashed before.'
                  f' Please review the file and delete it or rename it')
            sys.exit(1)
        self.output_filename = output_file
        self.output_file = None
        self.writer = None
        self.headers = ["subject", "session", "scan", "image", "tag"]

        if input_filename:
            self.logger.info(f"File provided, reading {input_filename}")
            with open(str(input_filename)) as f:
                metadata = f.readline()
                metadata = metadata[1:]
                metadata = metadata.split(",")

                self.xnat_url = metadata[0].split("=")[1].strip()
                self.project = metadata[1].split("=")[1].strip()
                self.logger.debug(f"Detected xnat data: url={self.xnat_url}, project={self.project}")
                reader = csv.DictReader(f, delimiter='\t')
                initial_data = [d for d in reader]

                self.url_getter = XNATUrl(self.xnat_url, self.project)
                self.session = Session(xnat_user, xnat_pass)

        else:
            self.logger.info(f"No file provided, getting data from xnat {xnat_url} with project {xnat_project}")
            self.xnat_url = xnat_url
            self.project = xnat_project
            self.url_getter = XNATUrl(xnat_url, xnat_project)
            self.session = Session(xnat_user, xnat_pass)

            initial_data = self.get_data_from_xnat(self.session,
                                                   self.url_getter,
                                                   modality_whitelist=["xnat:dxSessionData", "xnat:crSessionData"])

        self.tagged_data = [d for d in initial_data if "tag" in d and d["tag"] != ""]
        self.data = [d for d in initial_data if "tag" not in d or d["tag"] == ""]
        self.actual_data = 0
        self.logger.debug(f"Ended loading data. Found {len(self.tagged_data)} tagged and {len(self.data)} untagged data"
                          )

        self.actual_img = 0
        self.num_img = 0
        self.images_in_process = 0
        self.images = [None] * n_buffer
        self.data_link = [-1] * n_buffer



        self._num_img_lock = threading.Lock()

        self.threads = list()

    def __enter__(self):
        self.logger.debug("Opening output file")
        self.output_file = open(self.output_filename_lock, "w")
        self.output_file.write("#url={},project={}\n".format(self.xnat_url, self.project))

        self.writer = csv.DictWriter(self.output_file, fieldnames=self.headers, delimiter='\t')
        self.writer.writeheader()
        for d in self.tagged_data:
            self.writer.writerow(d)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info(f"Storing output data in file {self.output_filename_lock}")
        for d in self.data:
            if "tag" not in d or d["tag"] == "":
                self.writer.writerow(d)
        self.output_file.close()
        if not exc_type:
            os.replace(self.output_filename_lock, self.output_filename)

    def run(self):
        for index in range(4):
            x = threading.Thread(target=daemon, args=(self,), daemon=True)
            self.threads.append(x)
            x.start()
        self.ui.run()

    def tag_actual(self, option):
        with self._num_img_lock:
            if self.num_img != 0:
                actual_data = self.data_link[self.actual_img]
                self.logger.info(
                    f'Tagged data {self.data[actual_data]} at position {actual_data} with option {option}')

                self.data[actual_data]["tag"] = option
                self.writer.writerow(self.data[actual_data])

                self.num_img -= 1
                self.actual_img = (self.actual_img + 1) % len(self.images)

                if self.num_img == 0:
                    self.ui.show_wait_img()
                else:
                    self.logger.info(f"Showing data {self.data[self.data_link[self.actual_img]]}")
                    self.ui.refresh_img(self.images[self.actual_img])

    def ask_new_image(self):
        with self._num_img_lock:
            self.logger.debug(f'Asking new image ({self.num_img}+{self.images_in_process}/{len(self.images)}) {self.actual_data}/{len(self.data)} ')
            if self.num_img + self.images_in_process >= len(self.images) - 1 or self.actual_data >= len(self.data):
                return -1, None
            self.images_in_process += 1
            actual_data = self.actual_data
            self.actual_data += 1
            data = self.data[actual_data]
            self.logger.debug(self.url_getter
                                  .get_subject(data["subject"])
                                  .get_experiment(data["session"])
                                  .get_scan(data["scan"])
                                  .get_resource("DICOM")
                                  .get_file(data["image"]))
            if data["image"].endswith(".dcm"):
                return actual_data, (self.url_getter
                                          .get_subject(data["subject"])
                                          .get_experiment(data["session"])
                                          .get_scan(data["scan"])
                                          .get_resource("DICOM")
                                          .get_file(data["image"]))

            elif data["image"].endswith(".png"):
                return actual_data, (self.url_getter
                                          .get_subject(data["subject"])
                                          .get_experiment(data["session"])
                                          .get_scan(data["scan"])
                                          .get_resource("PNG")
                                          .get_file(data["image"]))

    def store_new_image(self, img_index, data):
        with self._num_img_lock:
            self.logger.debug(f"Storing new image at {img_index}")

            self.images[(self.actual_img + self.num_img) % len(self.images)] = data
            self.data_link[(self.actual_img + self.num_img) % len(self.images)] = img_index

            if self.num_img == 0:
                self.logger.info(f"Showing data {self.data[self.data_link[self.actual_img]]}")
                self.ui.refresh_img(data)

            self.num_img = self.num_img + 1
            self.images_in_process -= 1

    def get_data_from_xnat(self, session, url_getter, modality_whitelist):
        data = []
        subjects = session.get(url_getter.get_subjects(file_type="json")).json()["ResultSet"]["Result"]
        self.logger.debug(f"Found {len(subjects)} subjects")
        for i, s in enumerate(subjects):
            self.logger.debug(f"Working on subject {s['ID']} ({i}/{len(subjects)})")
            sub_url = url_getter.get_subject(s["label"])
            experiments = session.get(sub_url.get_experiments(file_type="json")).json()["ResultSet"]["Result"]
            self.logger.debug(f"Found {len(experiments)} experiments")
            for e in experiments:
                self.logger.debug(f"Working on experiment {e['label']}")
                if e["xsiType"] not in modality_whitelist:
                    continue
                exp_url = sub_url.get_experiment(e["ID"])
                scans = session.get(exp_url.get_scans(file_type="json")).json()["ResultSet"]["Result"]
                self.logger.debug(f"Found {len(scans)} scans")
                for sc in scans:
                    self.logger.debug(f"Working on scan {sc['ID']}")
                    scan_url = exp_url.get_scan(sc["ID"])
                    files = session.get(scan_url.get_resource("DICOM")
                                                .get_files(file_type="json")
                                        ).json()["ResultSet"]["Result"]
                    for f in files:
                        data.append({
                            "subject": s["label"],
                            "session": e["label"],
                            "scan": sc["ID"],
                            "image": f["Name"],
                            "tag": ""
                        })
        return data
