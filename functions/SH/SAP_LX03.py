# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(con, delivery_number, total_stock):
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
        session.findById("wnd[0]/usr/ctxtS1_LGTYP-LOW").text = "916"
        session.findById("wnd[0]/usr/ctxtS1_LGPLA-LOW").text = f'00{delivery_number}'
        session.findById("wnd[0]/usr/ctxtP_VARI").text = "/zdel"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()

        # serial = session.findById("wnd[0]/usr/lbl[5,7]").Text
        # cantidad = session.findById("wnd[0]/usr/lbl[32,7]").Text
        #############

        original_position = 0
        real_stock = 0
        max_scroll = session.findById("wnd[0]/usr").verticalScrollbar.Maximum

        try:
            y = 7
            while True:
                session.findById(f'wnd[0]/usr/lbl[5,{y}]')
                y += 1
                original_position += 1
        except:
            pass
        try:
            info_list = []
            while True:
                y = 7
                for x in range(original_position):
                    real_stock += int(session.findById(f'wnd[0]/usr/lbl[32,{y}]').Text.strip().replace(",000", "").replace(".000", "").replace(",", ""))
                    q = {
                        "storage_unit": session.findById(f'wnd[0]/usr/lbl[5,{y}]').Text,
                        "stock":  session.findById(f'wnd[0]/usr/lbl[32,{y}]').Text.strip().replace(",000", "").replace(".000", "").replace(",", "")
                    }

                    y += 1
                    info_list.append(q)
                if max_scroll != 0:
                    session.findById("wnd[0]/usr").verticalScrollbar.position += original_position
                else:
                    raise Exception("Nothing to do here")

        except Exception as error:
            pass
        #############
        # session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        # session.findById("wnd[0]").sendVKey(0)

        if int(total_stock) != int(real_stock):
            response = {"result": "N/A", "error": f'Shipment Quantity: {total_stock}, Delivery Quantity: {real_stock}'}
            return json.dumps(response)
        response = {"result": info_list, "error": "N/A"}
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
    print(Main("80692028", "1800"))

# -End-------------------------------------------------------------------
