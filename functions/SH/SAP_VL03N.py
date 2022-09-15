# -Sub Main--------------------------------------------------------------
def Main(con, delivery):
    import sys
    import win32com.client
    import json
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nVL03N"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtLIKP-VBELN").text = delivery
        session.findById("wnd[0]/tbar[1]/btn[18]").press()
        try:
            try:
                session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-HISTU[0,0]").setFocus()
            except:
                session.findById("wnd[0]/mbar/menu[2]/menu[0]/menu[4]").select()
                pass
        except:
            error = session.findById("wnd[0]/sbar").Text
            response = {"result": "N/A", "error": error}
            return json.dumps(response)

        response = {"result": "OK", "error": "N/A"}
        return json.dumps(response)
    except Exception as e:
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
    print(Main(0, '80770108'))

# -End-------------------------------------------------------------------
