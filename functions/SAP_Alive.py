# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------
import sys



# -Sub Main--------------------------------------------------------------
def Main():
    import win32com.client
    import json
    import pythoncom
    try:
        pythoncom.CoInitialize()
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        if not type(SapGuiAuto) == win32com.client.CDispatch:
            return

        application = SapGuiAuto.GetScriptingEngine
        if not type(application) == win32com.client.CDispatch:
            SapGuiAuto = None
            return

        connection = application.Children(0)
        if not type(connection) == win32com.client.CDispatch:
            application = None
            SapGuiAuto = None
            return

        if connection.DisabledByServer == True:
            application = None
            SapGuiAuto = None
            return

        session = connection.Children(0)
        if not type(session) == win32com.client.CDispatch:
            connection = None
            application = None
            SapGuiAuto = None
            return

        if session.Info.IsLowSpeedConnection == True:
            connection = None
            application = None
            SapGuiAuto = None
            return

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


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main()

# -End-------------------------------------------------------------------
