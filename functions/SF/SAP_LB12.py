# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(con, serial_num):
    """
    Function process material document
    Transfering the serial number from storage type 901 to storage type VUL/V01
    """
    import win32com.client
    import json
    import pythoncom
    try:
        pythoncom.CoInitialize()

        SapGuiAuto = win32com.client.GetObject("SAPGUI")

        application = SapGuiAuto.GetScriptingEngine

        connection = application.Children(con)

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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLB12"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[44]").press()
        # session.findById("wnd[0]/usr/ctxtRL03T-LETY2").text = "001"
        # session.findById("wnd[0]/usr/ctxtRL03T-LGTY2").text = "VUL"
        # session.findById("wnd[0]/usr/ctxtRL03T-LGTY2").setFocus()
        # session.findById("wnd[0]/usr/ctxtRL03T-LGTY2").caretPosition = 3
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/usr/ctxtLTAP-LETYP").text = "001"
        session.findById("wnd[0]/usr/ctxtLTAP-LDEST").text = "dummy"
        session.findById("wnd[0]/usr/ctxtLTAP-NLTYP").text = "VUL"
        session.findById("wnd[0]/usr/ctxtLTAP-NLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-NLPLA").text = "V01"
        session.findById("wnd[0]/usr/ctxtLTAP-NLENR").text = f'0{serial_num}'
        # session.findById("wnd[0]/usr/ctxtLTAP-NLENR").setFocus()
        # session.findById("wnd[0]/usr/ctxtLTAP-NLENR").caretPosition = 10
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        result = session.findById("wnd[0]/sbar/pane[0]").Text

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)


        response = {"result": f'{result}', "error": "N/A"}

        return (json.dumps(response))

    except:
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
    Main("174968934")

# -End-------------------------------------------------------------------
