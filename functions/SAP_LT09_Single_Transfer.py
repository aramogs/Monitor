# -Begin-----------------------------------------------------------------

# -Sub Main--------------------------------------------------------------

def Main(serial_num, storage_type, storage_bin):
    """
    Function takes a list of storage units and transfers them to the storage type nad bin selected
    """
    import json
    import re
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


        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT09"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/txtLEIN-LENUM").text = f'{serial_num}'
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxt*LTAP-NLTYP").text = storage_type
        session.findById("wnd[0]/usr/txt*LTAP-NLPLA").text = storage_bin
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        result = session.findById("wnd[0]/sbar/pane[0]").Text
        # Getting only the transfer order and not the text
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass
        response = {"result": f'{result}', "error": "N/A"}

        return json.dumps(response)


    except:
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)

        return (json.dumps(response))

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("0171349693", "MP1", "P0501")

# -End-------------------------------------------------------------------
