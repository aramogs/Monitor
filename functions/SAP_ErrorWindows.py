import ctypes
import json
import pygetwindow as gw
import win32con
import win32gui


error_window = ["SAP GUI for Windows 730", "SAP GUI for Windows 740", "SAP GUI for Windows 760", "SAP GUI for Windows 800", "MessageBox", "Print", "SAP Logon for Windows has stop working"]

# Get a list of all open windows
windows = gw.getAllTitles()


def error_windows():
    for window_title in windows:
        for error_title in error_window:
            if error_title == window_title:
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
