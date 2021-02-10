# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------



# -Sub Main--------------------------------------------------------------
def Main(printer, serial_num):
    import json
    import sys
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZ_UC_WM"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtP_VSTEL").text = "5210"
        session.findById("wnd[0]/usr/ctxtP_EXIDV").text = serial_num
        session.findById("wnd[0]/usr/ctxtP_DDEST").text = printer
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZ_UC_WM"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtP_VSTEL").text = "5210"
        session.findById("wnd[0]/usr/ctxtP_EXIDV").text = serial_num
        session.findById("wnd[0]/usr/ctxtP_DDEST").text = printer
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        response = {"result": "OK", "error": "N/A"}
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

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("dummy", "S567")
# -End-------------------------------------------------------------------
