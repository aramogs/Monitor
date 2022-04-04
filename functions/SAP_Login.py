
#-Begin-----------------------------------------------------------------

#-Includes--------------------------------------------------------------

#-Sub Main--------------------------------------------------------------
def Main():
    """
    Function opens SAP and access it as a user depending on .env file
    """
    import win32com.client
    import subprocess
    import ctypes
    import time
    import json
    import os
    import pythoncom

    try:
        pythoncom.CoInitialize()
        path = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
        subprocess.Popen(path,stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)

        # Necesario par correr win32com.client en Threading
        # pythoncom.CoInitialize()

        sapmin = ctypes.windll.user32.FindWindowW(None, "SAP Logon 760")
        ctypes.windll.user32.ShowWindow(sapmin, 6)

        sapmin = ctypes.windll.user32.FindWindowW(None, "SAP Logon 740")
        ctypes.windll.user32.ShowWindow(sapmin, 6)

        SapGuiAuto = win32com.client.GetObject('SAPGUI')
        if not type(SapGuiAuto) == win32com.client.CDispatch:
            return

        application = SapGuiAuto.GetScriptingEngine
        if not type(application) == win32com.client.CDispatch:
            SapGuiAuto = None
            return
        connection = application.OpenConnection(os.getenv("SAP_NAME"), True)

        if not type(connection) == win32com.client.CDispatch:
            application = None
            SapGuiAuto = None
            return

        session = connection.Children(0)
        if not type(session) == win32com.client.CDispatch:
            connection = None
            application = None
            SapGuiAuto = None
            return

        session.findById("wnd[0]/usr/txtRSYST-MANDT").text = "200"
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = os.getenv("SAP_USER")
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = os.getenv("SAP_PASS")
        session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "EN"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[1]/usr/radMULTI_LOGON_OPT1").select()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        time.sleep(5)
        response = {"sap_status": "ok"}
        return (json.dumps(response))
    except:
        response = {"sap_status": "error"}
        return (json.dumps(response))
    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None

#-Main------------------------------------------------------------------
if __name__ == '__main__':
    Main()
#-End-------------------------------------------------------------------
