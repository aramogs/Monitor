# -Sub Main--------------------------------------------------------------
def Main(masters):
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nHU03"
        session.findById("wnd[0]").sendVKey(0)
        ##########################
        n = 0
        for master in masters:
            session.findById(f'wnd[0]/usr/tblRHU_DISPLAY_HANDLING_UNITSTC_HU_ANZ/ctxtVEKP-EXIDV[0,{n}]').Text = master["storage_unit"]
            n += 1
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        if len(masters) == 1:
            session.findById("wnd[0]/mbar/menu[2]/menu[0]/menu[4]").select()
        ########################sapscript find by name

        original_position = 0
        iterations = 0
        max_scroll = session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005").verticalScrollbar.Maximum
        try:
            for x in range(max_scroll):
                session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-HISTU[0,{x}]')
                original_position += 1
        except:
            pass

        iterations = math.ceil(max_scroll/original_position)
        # print(f'MAX: {max_scroll}')
        # print(f'Original {original_position}')
        # print(f'Iterations {iterations}')
        text_iterations = {}
        text_iterations2 = {}
        iterations_list = []

        for x in range(original_position):
            text_iterations["iteration{0}".format(x)] = f'session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-HISTU[0,{x}]").Text.strip()'
            text_iterations2["iteration{0}".format(x)] = f'session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-IDENT[1,{x}]").Text.strip()'
        for i in range(iterations):
            for (key, value), (key2, value2) in zip(text_iterations.items(), text_iterations2.items()):
                try:
                    iterations_list.append({f'{int(eval(value))}': f'{eval(value2)}'})
                except Exception as error:
                    pass
            try:
                session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005").verticalScrollbar.position += original_position
            except:
                pass
        levels = []
        serials = []
        info_list = []
        x = 0
        y = 0
        for index in range(len(iterations_list)):
            for level, serial_num in iterations_list[index].items():
                level = int(level)
                if level == 0 or level == 1 and len(serial_num) == 9:
                    if level == 0:
                        if y == 1:
                            y = 0
                            info_list.append({"master": f"{serial_master}", "serials": serials})
                            serials = []
                        serial_master = serial_num
                        y += 1

                    else:
                        serials.append(serial_num)
                x += 1
        # In case there is only one master then add the information to the response
        if len(info_list) == 0:
            info_list.append({"master": f"{serial_master}", "serials": serials})
        response = json.dumps({"result": f"{info_list}", "error": "N/A"})

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
    Main([{'storage_unit': '0178010857', 'stock': '   72'}])

# -End-------------------------------------------------------------------
