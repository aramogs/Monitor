import os
import platform
import webbrowser
from ctypes import windll
from tkinter import *
from tkinter import ttk

import center_tk_window
from setproctitle import setproctitle

setproctitle('Monitor')
windll.shell32.SetCurrentProcessExplicitAppUserModelID("app_icon")


class MainApplication:
    def __init__(self, parent):
        self._img_icon = "./img/image.ico"
        self._model = os.popen("wmic csproduct get name").read().replace("\n", "").replace("  ", "").replace("Name", "")
        self._service_tag = os.popen("wmic bios get serialnumber").read().replace("\n", "").replace("  ", "").replace(
            " ", "").replace("SerialNumber", "")
        self._my_system = platform.uname()
        self._background_color = "#152532"
        self._text_color = "#FCBD1E"
        self._logo_image = PhotoImage(file=r"./img/logo.png").subsample(10, 10)

        self.parent = parent
        self.parent.title("Monitor")
        self.parent.geometry("500x600")
        self.parent.configure(bg=self._background_color)
        self.parent.iconbitmap(self._img_icon)

        self._line_style = ttk.Style()
        self._line = ttk.Separator(
            self.parent, orient=VERTICAL, style="Line.TSeparator")

        self._labelGI = Label(self.parent, text="General Info", bg=self._background_color)
        self._labelName = Label(self.parent, text="Computer Name:\t  {}".format(self._my_system.node),
                                bg=self._background_color)
        self._labelUser = Label(self.parent, text="User Name:\t  {}".format(os.environ['USERNAME']),bg=self._background_color)
        self._labelModel = Label(self.parent, text="Machine Model:\t  {}".format(self._model), bg=self._background_color)
        self._labelSerial = Label(self.parent, text="Service Tag:\t  {}".format(self._service_tag),
                                  bg=self._background_color, cursor="hand2")
        self._labelSerial = Label(self.parent, text="Service Tag:\t  {}".format(self._service_tag),
                                  bg=self._background_color, cursor="hand2")
        self._labelSerial.bind("<Button-1>", lambda e: self.dell_support(self._service_tag))
        self._labelOs = Label(self.parent,
                              text="System Info:\t  {} {} {} {}".format(self._my_system.system, self._my_system.release,
                                                                        self._my_system.machine,
                                                                        self._my_system.version),
                              bg=self._background_color)
        self._label = Label(self.parent, image=self._logo_image, bg="#152532")
        self._frame = LabelFrame(self.parent, text="", width=300)

        self._labelGI.configure(fg=self._text_color)
        self._line_style.configure("Line.TSeparator", background=self._text_color)
        self._labelName.configure(fg=self._text_color)
        self._labelUser.configure(fg=self._text_color)
        self._labelModel.configure(fg=self._text_color)
        self._labelSerial.configure(fg=self._text_color)
        self._labelOs.configure(fg=self._text_color)
        self._frame.configure(bg=self._background_color)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(8, weight=1)
        self._frame.columnconfigure(0, weight=1)
        self._frame.rowconfigure(7, weight=1)

        self._label.grid(row=0, column=0, columnspan=2, padx=90, pady=10)
        self._labelGI.grid(row=1, column=0, columnspan=1, padx=5, pady=.5, sticky=W)
        self._line.grid(row=2, columnspan=2, sticky=E + W)
        self._labelName.grid(row=3, column=0, padx=5, pady=.5, sticky=W)
        self._labelUser.grid(row=4, column=0, padx=5, pady=.5, sticky=W)
        self._labelModel.grid(row=5, column=0, padx=5, pady=.5, sticky=W)
        self._labelSerial.grid(row=6, column=0, padx=5, pady=.5, sticky=W)
        self._labelOs.grid(row=7, column=0, padx=5, pady=.5, sticky=W)
        self._frame.grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky=E + W + N + S)

        self.parent.wm_attributes("-alpha", .9)
        self.parent.resizable(False, True)
        # self.parent.protocol("WM_DELETE_WINDOW", self.withdraw_window)

        center_tk_window.center_on_screen(self.parent)

    @staticmethod
    def dell_support(serial):
        url = "http://www.dell.com/support/home/product-support/servicetag/{}".format(
            serial)
        webbrowser.open_new(url)


class SecondaryWindow:
    def __init__(self, parent, secondary):
        self.parent = parent
        self.secondary = secondary
        self._background_color = "#152532"
        self._text_color = "#FCBD1E"

        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        secondary.overrideredirect(1)
        secondary.geometry("550x50+{0}+{1}".format(screen_width - 550, screen_height - 80))
        secondary.configure(background='#152532')

        # secondary.wm_attributes("-alpha", .9)


if __name__ == "__main__":
    master: Tk = Tk()
    mainApp = MainApplication(master)
    secondaryApp = SecondaryWindow(master, Toplevel())
    master.mainloop()
