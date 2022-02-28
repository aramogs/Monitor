import ctypes
import json

import win32con
import win32gui

error_window = ["SAP GUI for Windows 730", "SAP GUI for Windows 740", "SAP GUI for Windows 760", "MessageBox", "Print","error.log"
                "SAP Logon for Windows has stop working"]
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
    for title in titles:
        for error_title in error_window:
            if error_title == title:
                print(f'"Error Window Found {error_title}"')
                window = (win32gui.FindWindow(None, f'{error_title}'))
                win32gui.PostMessage(window, win32con.WM_CLOSE, 0, 0)
                print(f'"Error Window Closed {error_title}"')

                response = {"Error Window Found and closed": error_title}
                return json.dumps(response)


# def monitor_visible():
#     global titles
#     titles = []
#     enum_windows(enum_window_process(foreach_window), 0)
#     for title in titles:
#         if title != "":
#             print(title)
#         # if 'Monitor' in title:
#         #     print(title)
#         #     return True
# -Main------------------------------------------------------------------
if __name__ == '__main__':
  error_windows()

# -End-------------------------------------------------------------------
