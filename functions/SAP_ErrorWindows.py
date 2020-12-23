import ctypes
import json

import win32con
import win32gui

error_window = ["SAP GUI for Windows 730", "SAP GUI for Windows 740", "SAP GUI for Windows 760", "MessageBox", "Print"]
titles = []

enum_windows = ctypes.windll.user32.EnumWindows
enum_window_process = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
get_window_text = ctypes.windll.user32.GetWindowTextW
get_window_text_length = ctypes.windll.user32.GetWindowTextLengthW
is_window_visible = ctypes.windll.user32.IsWindowVisible


def foreach_window(hwnd, lParam):

    if is_window_visible(hwnd):
        length = get_window_text_length(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        get_window_text(hwnd, buff, length + 1)
        titles.append(buff.value)
    return True





def error_windows():

    enum_windows(enum_window_process(foreach_window), 0)
    for w in titles:
        for z in error_window:
            if z == w:
                # print(f'"Error Window Found {z}"')
                window = (win32gui.FindWindow(None, f'{z}'))
                win32gui.PostMessage(window, win32con.WM_CLOSE, 0, 0)
                # print(f'"Error Window Closed {z}"')

                response = {"Error Window Found and closed": z}
                return (json.dumps(response))


def monitor_visible():
    global titles
    titles = []
    enum_windows(enum_window_process(foreach_window), 0)
    for title in titles:
        if title != "":
            print(title)
        # if 'Monitor' in title:
        #     print(title)
        #     return True


