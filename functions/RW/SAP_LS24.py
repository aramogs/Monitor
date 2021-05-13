# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------
# -Sub Main--------------------------------------------------------------

def Main(sap_num, storage_type, storage_bin):
    import sys
    import win32com.client
    import json
    import pythoncom
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

        # session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLS24"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRL01S-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtRL01S-MATNR").text = sap_num
        session.findById("wnd[0]/usr/ctxtRL01S-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtRL01S-BESTQ").text = "*"
        session.findById("wnd[0]/usr/ctxtRL01S-SOBKZ").text = "*"
        session.findById("wnd[0]/usr/ctxtRL01S-LGTYP").text = storage_type
        session.findById("wnd[0]/usr/ctxtRL01S-LGPLA").text = storage_bin
        session.findById("wnd[0]/usr/ctxtRL01S-LISTV").text = "/DEL"
        session.findById("wnd[0]").sendVKey(0)

        try:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
            if error != "":
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
                session.findById("wnd[0]/tbar[0]/btn[15]").press()
                response = {"result": "N/A", "error": error}
                return json.dumps(response)
            else:
                raise Exception('I know Python!')
        except:
            try:
                quantity = session.findById("wnd[0]/usr/lbl[35,8]").Text

            except:
                pass
            session.findById("wnd[0]/tbar[0]/btn[15]").press()
            session.findById("wnd[0]/tbar[0]/btn[15]").press()

            response = {"result": int(float(re.sub(r",", "", quantity).strip())), "error": "N/A"}

            return json.dumps(response)

    except Exception as e:
        print(e)
        # print(sys.exc_info()[0])
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

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
    print(Main("5V0005305195", "102", "103"))
# -End-------------------------------------------------------------------
