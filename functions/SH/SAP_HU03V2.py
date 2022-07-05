# -Sub Main--------------------------------------------------------------
def Main(con):
    try:
        # print("MASTERS:", masters)
        import sys
        import win32com.client
        import json
        import time
        import math
        import traceback

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

        original_position = 0
        iterations = 0
        max_scroll = session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005").verticalScrollbar.Maximum
        try:
            while True:
                if session.findById(
                        f"wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-IDENT[1,{original_position}]").Text == "____________________":
                    raise Exception("Not what we are looking for")
                original_position += 1
        except:
            pass

        iterations = math.ceil(max_scroll / original_position)
        # print(f'MAX: {max_scroll}')
        # print(f'Original {original_position}')
        # print(f'Iterations {iterations}')
        text_iterations = {}
        text_iterations2 = {}
        text_iterations3 = {}
        text_iterations4 = {}
        iterations_list = []

        for x in range(original_position):
            text_iterations["iteration{0}".format(x)] = f'session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-HISTU[0,{x}]").Text.strip()'
            text_iterations2["iteration{0}".format(x)] = f'session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-IDENT[1,{x}]").Text.strip()'
            text_iterations3["iteration{0}".format(x)] = f'session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-QUANTITY[3,{x}]").Text.strip()'
            text_iterations4["iteration{0}".format(x)] = f'session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-MATNR[2,{x}]").Text.strip()'




        for i in range(iterations):
            for (key, value), (key2, value2), (key3, value3), (key4, value4) in zip(text_iterations.items(), text_iterations2.items(), text_iterations3.items(), text_iterations4.items()):
                try:
                    iterations_list.append({f'{int(eval(value))}': [f'{eval(value2)}', f'{eval(value3)}', f'{eval(value4)}']})
                except Exception as error:
                    # print(error)
                    pass
            try:
                # session.findById("wnd[0]/tbar[0]/btn[82]").press()
                session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005").verticalScrollbar.position += original_position
            except:
                pass
        levels = []
        serials = []
        info_list = []
        real_quantity = 0
        test = 0
        x = 0
        y = 0

        # Se agrega iteracion extra para que procese el ultimo punto
        iterations_list.append({f'{int(eval("0"))}': [f'{eval("123456789")}', f'{eval("0")}', f'{eval("70000000000")}']})

        for index in range(len(iterations_list)):
            for level, serial_quantity in iterations_list[index].items():
                if int(serial_quantity[1].strip().replace(",000", "").replace(".000", "").replace(",", "")) > 1:
                    test += int(serial_quantity[1].strip().replace(",000", "").replace(".000", "").replace(",", ""))
                level = int(level)
                if level == 0 or level == 1 and len(serial_quantity[0]) == 9:
                    if level == 0:
                        if y == 1:
                            y = 0
                            info_list.append({"master": f"{serial_master}", "serials": serials})
                            serials = []
                        serial_master = serial_quantity[0]
                        y += 1

                    else:
                        serials.append(serial_quantity[0])

                if level == 2:
                    real_quantity += int(serial_quantity[1].strip().replace(",000", "").replace(".000", "").replace(",", ""))
                if level == 1:
                    if len(serial_quantity[2]) > 10:
                        real_quantity += int(serial_quantity[1].strip().replace(",000", "").replace(".000", "").replace(",", ""))
                x += 1
        # In case there is only one master then add the information to the response
        if len(info_list) == 0:
            info_list.append({"master": f"{serial_master}", "serials": serials, "real_quantity": f"{real_quantity}"})
            print(info_list)
        response = json.dumps({"result": f"{info_list}", "error": "N/A", "real_quantity": f"{real_quantity}"})
        return response

    except Exception:
        print(traceback.format_exc())


    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    # print(Main([{'storage_unit': '0178010857', 'stock': '72'},{'storage_unit': '0177482588', 'stock': '72'}]))
    print(Main())

# -End-------------------------------------------------------------------
