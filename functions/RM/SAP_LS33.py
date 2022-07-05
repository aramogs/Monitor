# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(con, storage_unit):
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLS33"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/txtLEIN-LENUM").text = storage_unit
        session.findById("wnd[0]").sendVKey(0)
        storage_type = session.findById("wnd[0]/usr/ctxtLEIN-LGTYP").Text
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        response = {"storage_type": storage_type, "error": "N/A"}
        return json.dumps(response)

    except Exception as e:

        if session.Children.Count == 2:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()

        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"storage_type": "N/A",  "error": error}
        # session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        # session.findById("wnd[0]").sendVKey(0)

        return json.dumps(response)

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("0177996867")
# -End-------------------------------------------------------------------

