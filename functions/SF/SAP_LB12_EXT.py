# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------
# -Sub Main--------------------------------------------------------------
def Main(con, serial):
    import json
    import sys
    import win32com.client
    import re
    try:

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
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/usr/ctxtLTAP-LETYP").text = "001"
        session.findById("wnd[0]/usr/ctxtLTAP-LDEST").text = "dummy"
        session.findById("wnd[0]/usr/ctxtLTAP-NLTYP").text = "EXT"
        session.findById("wnd[0]/usr/ctxtLTAP-NLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-NLPLA").text = "TEMPB"
        session.findById("wnd[0]/usr/ctxtLTAP-NLENR").text = f'0{serial}'
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)
        result = session.findById("wnd[0]/sbar/pane[0]").Text
        if result != "":

            response = {"serial_num": serial, "result": "N/A", "error": result}
            session.findById("wnd[0]/tbar[0]/btn[11]").press()
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
        else:
            session.findById("wnd[0]/tbar[0]/btn[11]").press()
            result = session.findById("wnd[0]/sbar/pane[0]").Text

            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
            response = {"serial_num": serial, "result": result, "error": "N/A"}

        # response = {"result": f'{result}', "error": "N/A"}
        print(response)
        return json.dumps(response)

    except Exception as e:
        try:
            error = session.findById("wnd[1]/usr/txtSPOP-TEXTLINE1").Text
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
            session.findById("wnd[0]/tbar[0]/btn[12]").press()
            session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        except:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"serial_num": "N/A", "result": "N/A", "error": error}

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
    Main()

# -End-------------------------------------------------------------------
