import io
import time

import numpy
import pydicom
from PIL import Image


def daemon(app):
    while True:
        download_img_index, download_url = app.ask_new_image()
        if download_img_index != -1:

            r = app.session.get(download_url)
            f = io.BytesIO(r.content)

            if str(download_url).endswith(".dcm"):
                ds = pydicom.dcmread(f, force=True)
                img = ds.pixel_array

            else:
                img = numpy.array(Image.open(f))

            app.store_new_image(download_img_index, img)

        else:
            time.sleep(0.5)
