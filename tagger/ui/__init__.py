import tkinter

import numpy
from pkg_resources import resource_filename
from PIL import Image, ImageTk
import cv2


class UI:
    def __init__(self, options, app):
        self.app = app
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window)
        self.wait_img = tkinter.PhotoImage(str(resource_filename(__name__, 'resources/sand-clock-svgrepo-com.svg')))
        self.image_on_canvas = self.canvas.create_image(0, 0,
                                                        anchor=tkinter.NW,
                                                        image=self.wait_img)
        self.canvas.pack(fill="both", expand=True)

        frame = tkinter.Frame(self.window)
        frame.pack()
        self.option_buttons = [tkinter.Button(self.window,
                                              text=o["text"],
                                              command=lambda option=o["option"]: self.app.tag_actual(option))
                               for o in options
                               ]

        for b in self.option_buttons:
            b.pack()

        self.img = None

    def run(self):
        self.window.mainloop()

    def show_wait_img(self):
        self.canvas.itemconfig(self.image_on_canvas, image=self.wait_img)

    def refresh_img(self, np_array):
        self.canvas.update()
        max_value = np_array.max()
        min_value = np_array.min()
        np_array = (np_array - min_value) / (max_value - min_value)
        np_array *= 255
        #info = numpy.iinfo(np_array.dtype)  # Get the information of the incoming image type
        #np_array = np_array.astype(numpy.float64) / info.max  # normalize the data to 0 - 1
        #np_array = 255 * np_array  # Now scale by 255
        np_array = np_array.astype(numpy.uint8)

        img = Image.fromarray(cv2.resize(np_array, dsize=(self.canvas.winfo_width(), self.canvas.winfo_height()),
                                         interpolation=cv2.INTER_CUBIC))
        self.img = ImageTk.PhotoImage(image=img)
        self.canvas.itemconfig(self.image_on_canvas, image=self.img)
