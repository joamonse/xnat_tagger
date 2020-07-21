

class XNATUrl:
    def __init__(self, url, proj):
        if url[-1] == "/":
            url = url[:-1]
        self.url = "{}/data/projects/{}".format(url, proj)

    def __repr__(self):
        return self.url

    def get_subjects(self, file_type="csv"):
        return "{}/subjects?format={}".format(self.url, file_type)

    def get_experiments(self, file_type="csv"):
        return "{}/experiments?format={}".format(self.url, file_type)

    def get_subject(self, subject):
        return Subject("{}/subjects/{}".format(self.url, subject))

    def get_experiment(self, experiment):
        return Experiment("{}/experiments/{}".format(self.url, experiment))

    def get_pipeline(self, pipeline):
        return Pipelines(f"{self.url}/pipelines/{pipeline}")

    def get_pipelines(self, file_type="csv"):
        return Pipelines(f"{self.url}/pipelines?format={file_type}")


class Pipelines:
    def __init__(self, base_url):
        self.url = base_url

    def __repr__(self):
        return self.url

    def run(self, experiment):
        return f"{self.url}/experiments/{experiment}?match=LIKE"


class Subject:
    def __init__(self, base_url):
        self.url = base_url

    def __repr__(self):
        return self.url

    def get_experiments(self, file_type="csv"):
        return "{}/experiments?format={}".format(self.url, file_type)

    def get_experiment(self, experiment):
        return Experiment("{}/experiments/{}".format(self.url, experiment))


class Experiment:
    def __init__(self, base_url):
        self.url = base_url

    def __repr__(self):
        return self.url

    def get_scans(self, file_type):
        return "{}/scans?format={}".format(self.url, file_type)

    def get_scan(self, scan):
        return Scan("{}/scans/{}".format(self.url, scan))

    def get_resources(self, file_type):
        return "{}/resources?format={}".format(self.url, file_type)

    def get_resource(self, resource):
        return Resource("{}/resources/{}".format(self.url, resource))


class Scan(object):
    def __init__(self, base_url):
        self.url = base_url

    def __repr__(self):
        return self.url

    def get_resources(self, file_type):
        return "{}/resources?format={}".format(self.url, file_type)

    def get_resource(self, resource):
        return Resource("{}/resources/{}".format(self.url, resource))


class Resource:
    def __init__(self, base_url):
        self.url = base_url

    def __repr__(self):
        return self.url

    def get_files(self, file_type):
        return "{}/files?format={}".format(self.url, file_type)

    def get_file(self, file):
        return File("{}/files/{}".format(self.url, file))


class File:
    def __init__(self, base_url):
        self.url = base_url

    def __repr__(self):
        return self.url

    def overwrite(self):
        return self.url+"?overwrite=true"
