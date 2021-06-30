# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------



# -Sub Main--------------------------------------------------------------
def Main(material, cantidad, serial, plan_id):
    import sys
    import win32com.client
    import pythoncom
    import json
    import re
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


        session.findById("wnd[0]/tbar[0]/okcd").text = "/nMFBF"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/tabsTAB800/tabpLAGER/ssubTABSUB800:SAPLBARM:0801/ctxtRM61B-MATNR").text = material
        session.findById("wnd[0]/usr/subSUB800:SAPLBARM:0811/txtRM61B-ERFMG").text = cantidad
        session.findById("wnd[0]/usr/txtRM61B-BKTXT").text = f'EXT-{plan_id}'
        session.findById("wnd[0]/usr/tabsTAB800/tabpLAGER/ssubTABSUB800:SAPLBARM:0801/ctxtRM61B-VERID").text = "1"

        session.findById("wnd[0]/tbar[0]/btn[11]").press()

        result = session.findById("wnd[0]/sbar/pane[0]").Text
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        if "GR and GI" in result:
            response = {"serial_num": serial, "result": int(re.sub(r"\D", "", result, 0)), "error": "N/A"}
        else:
            response = {"serial_num": serial, "result": 'N/A', "error": f'{result}'}


        return json.dumps(response)

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
    Main("5000010057A0","2")

# -End-------------------------------------------------------------------
