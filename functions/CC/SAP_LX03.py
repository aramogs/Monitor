# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(con, storage_location, storage_type, storage_bin):
    import win32com.client
    import pythoncom
    import json
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLX03"
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/ctxtS1_LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtS1_LGTYP-LOW").text = storage_type
        session.findById("wnd[0]/usr/ctxtS1_LGPLA-LOW").text = storage_bin
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "/zdel"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        serial = session.findById("wnd[0]/usr/lbl[5,7]").Text
        #############

        original_position = 0
        maxScroll = session.findById("wnd[0]/usr").verticalScrollbar.Maximum
        try:
            y = 7
            while True:
                q = session.findById(f'wnd[0]/usr/lbl[5,{y}]').Text
                y += 1
                original_position += 1

        except:
            pass
        try:
            info_list = []
            while True:
                y = 7
                for x in range(original_position):
                    if storage_location == session.findById("wnd[0]/usr/lbl[65,7]").Text:
                        q = {
                            "storage_unit": session.findById(f'wnd[0]/usr/lbl[5,{y}]').Text
                        }
                        y += 1
                        info_list.append(q)
                if maxScroll != 0:
                    session.findById("wnd[0]/usr").verticalScrollbar.position += original_position
                else:
                    raise Exception("Nothing to do here")

        except Exception as error:
            pass
        #############
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        response = {"result": info_list, "error": "N/A"}
        # print(response)
        return json.dumps(response)
    except Exception as e:
        print(e)

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("FG","FM0205")

# -End-------------------------------------------------------------------
