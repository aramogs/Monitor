# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(con, storage_location, part_num):
    """
    Function used to check the available quantity of material
    In this case is used to check all the storage units corresponding the the Part Number and the FIFO dates
    """
    import json
    import win32com.client
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLS24"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRL01S-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtRL01S-MATNR").text = part_num
        session.findById("wnd[0]/usr/ctxtRL01S-WERKS").text = "5210"
        session.findById("wnd[0]/usr/txtRL01S-LGORT").text = storage_location
        session.findById("wnd[0]/usr/ctxtRL01S-BESTQ").text = "*"
        session.findById("wnd[0]/usr/ctxtRL01S-SOBKZ").text = "*"
        session.findById("wnd[0]/usr/ctxtRL01S-LGTYP").text = "VUL"
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
            # SAP 740 no detecta estas lineas asi que el sorteo de fechas se hace ahora en Javascript
            # session.findById("wnd[0]/usr/lbl[54,6]").setFocus
            # session.findById("wnd[0]/usr/lbl[54,6]").caretPosition = 3
            # session.findById("wnd[0]").sendVKey(2)
            # session.findById("wnd[0]/tbar[1]/btn[40]").press()
            original_position = 0
            maxScroll = session.findById("wnd[0]/usr").verticalScrollbar.Maximum
            try:
                y = 8
                for i in range(100):
                    q = session.findById(f'wnd[0]/usr/lbl[5,{y}]').Text
                    y += 1
                    original_position += 1

            except:
                pass
            try:
                info_list = []
                while 1 > 0:
                    y = 8
                    for x in range(original_position):
                        q = {
                            "storage_bin": session.findById(f'wnd[0]/usr/lbl[5,{y}]').Text,
                            "gr_date": session.findById(f'wnd[0]/usr/lbl[54,{y}]').Text,
                            "storage_unit": session.findById(f'wnd[0]/usr/lbl[65,{y}]').Text
                        }
                        y += 1
                        info_list.append(q)
                    if maxScroll != 0:
                        session.findById("wnd[0]/usr").verticalScrollbar.position += original_position
                    else:
                        raise Exception ("Nothing to do here")

            except Exception as error:
                pass


            session.findById("wnd[0]/tbar[0]/btn[15]").press()
            session.findById("wnd[0]/tbar[0]/btn[15]").press()
            response = {"result": info_list, "error": "N/A"}
            return json.dumps(response)


    except:
        # print(sys.exc_info()[0])
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

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
    Main("7000025767A0")

# -End-------------------------------------------------------------------
