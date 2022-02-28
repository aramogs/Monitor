# -Begin-----------------------------------------------------------------

# -Sub Main--------------------------------------------------------------

def Main(serial_num, to_Sbin):
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
        try:
            session.findById("wnd[0]/usr/txtLEIN-LENUM").text = f'{serial_num}'
            session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
            session.findById("wnd[0]").sendVKey(0)
            session.findById("wnd[0]/usr/ctxt*LTAP-NLTYP").text = "102"
            session.findById("wnd[0]/usr/txt*LTAP-NLPLA").text = to_Sbin
            session.findById("wnd[0]/tbar[0]/btn[11]").press()
            result = session.findById("wnd[0]/sbar/pane[0]").Text
            # Getting only the transfer order and not the text
            response = {"serial": serial_num, "result": int(re.sub(r"\D", "", result, 0)), "error": "N/A"}

        except:
            result = session.findById("wnd[0]/sbar/pane[0]").Text
            response = {"serial": serial_num, "result": "N/A", "error": result}

            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)


        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass


        return json.dumps(response)


    except:
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

        session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
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
    Main("0171349693")

# -End-------------------------------------------------------------------
