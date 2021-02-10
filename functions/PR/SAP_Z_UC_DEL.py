# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------



# -Sub Main--------------------------------------------------------------
def Main(printer):
    import sys
    import json
    import win32com.client
    import pythoncom
    try:
        pythoncom.CoInitialize()

        SapGuiAuto = win32com.client.GetObject("SAPGUI")

        application = SapGuiAuto.GetScriptingEngine

        connection = application.Children(0)

        if connection.DisabledByServer == True:
            print("Scripting is disabled by server")
            application = None
            SapGuiAuto = None
            return

        session = connection.Children(0)

        if session.Info.IsLowSpeedConnection == True:
            print("Connection is low speed")
            connection = None
            application = None
            SapGuiAuto = None
            return

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZ_UC_DEL"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/chkCOPY").selected = -1
        session.findById("wnd[0]/usr/ctxtV_DISPO").text = "001"
        session.findById("wnd[0]/usr/ctxtB_DISPO").text = "999"
        session.findById("wnd[0]/usr/ctxtP_LDEST").text = printer
        # session.findById("wnd[0]/usr/ctxtP_LDEST").setFocus()
        # session.findById("wnd[0]/usr/ctxtP_LDEST").caretPosition = 4
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        try:
            error = session.findById("wnd[1]/usr/txtMESSTXT1").Text
            session.findById("wnd[1]/tbar[0]/btn[0]").press()
            session.findById("wnd[0]/tbar[0]/btn[3]").press()
            response = {"result": "N/A", "error": error}
        except:
            response = {"result": "OK", "error": "N/A"}
            session.findById("wnd[0]/tbar[0]/btn[3]").press()

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)


        return json.dumps(response)

    except Exception as e:
        print(e)
        try:
            error = session.findById("wnd[1]/usr/txtSPOP-TEXTLINE1").Text
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
            session.findById("wnd[0]/tbar[0]/btn[12]").press()
            session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        except:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

        # session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        return json.dumps(response)

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("dummy")
# -End-------------------------------------------------------------------
