# -Sub Main--------------------------------------------------------------
def Main(masters):
    try:
        # print("MASTERS:", masters)
        import sys
        import win32com.client
        import json
        import time

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
        max_scroll = session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005").verticalScrollbar.Maximum
        # print(f'MAX: {max_scroll}')
        try:
            for x in range(max_scroll):
                session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-HISTU[0,{x}]')
                original_position += 1
        except:
            pass

        # print(f'Original {original_position}')
        try:

            x = 0
            y = 0
            info_list = []
            serials = []

            for i in range(max_scroll):
                level = int(session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-HISTU[0,{x}]').Text.strip())

                if level == 0 or level == 1 and len(session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-IDENT[1,{x}]').Text) == 9:
                    if level == 0:
                        if y == 1:
                            y = 0
                            info_list.append({"master:" f'{serial_master}', "serials:" f'{serials}'})
                            serials = []
                        session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005").verticalScrollbar.position += x
                        x = 0
                        serial = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-IDENT[1,{x}]').Text
                        serial_master = serial
                        y += 1

                    else:
                        serial_child = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005/txtHUMV4-IDENT[1,{x}]').Text
                        serials.append(serial_child)
                x += 1
                if x == original_position:
                    session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6INH/ssubTAB:SAPLV51G:6040/tblSAPLV51GTC_HU_005").verticalScrollbar.position += x
                    x = 0
        except Exception as error:
            if len(info_list) == 0:
                info_list.append({"master:" f'{serial_master}', "serials:" f'{serials}'})
            pass


        response = json.dumps({"result": f'{info_list}', "error": "N/A"})
        return response

    except Exception as e:
        pass

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main([{'storage_unit': '0178010857', 'stock': '   72'}])

# -End-------------------------------------------------------------------
