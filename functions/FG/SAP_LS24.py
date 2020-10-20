# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(part_num):
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLS24"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRL01S-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtRL01S-MATNR").text = part_num
        session.findById("wnd[0]/usr/ctxtRL01S-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtRL01S-BESTQ").text = "*"
        session.findById("wnd[0]/usr/ctxtRL01S-SOBKZ").text = "*"
        session.findById("wnd[0]/usr/ctxtRL01S-LGTYP").text = "FG"
        session.findById("wnd[0]/usr/ctxtRL01S-LISTV").text = "/DEL"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/lbl[58,6]").caretPosition = 6
        session.findById("wnd[0]").sendVKey(2)
        session.findById("wnd[0]/tbar[1]/btn[40]").press()


        try:
            list = []
            while 1 > 0:
                y = 8
                for i in range(45):
                    q = {
                        "storage_bin": session.findById(f'wnd[0]/usr/lbl[5,{y}]').Text,
                        "gr_date": session.findById(f'wnd[0]/usr/lbl[58,{y}]').Text,
                        "storage_unit": session.findById(f'wnd[0]/usr/lbl[69,{y}]').Text
                    }
                    y += 1
                    list.append(q)
                session.findById("wnd[0]/usr").verticalScrollbar.position += 45


        except:
            pass

        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        response = {"result": list, "error": "N/A"}
        return (json.dumps(response))
    except:
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
    print(len(Main("7000023287A0")))

# -End-------------------------------------------------------------------