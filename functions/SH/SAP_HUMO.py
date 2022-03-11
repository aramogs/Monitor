# -Sub Main--------------------------------------------------------------
def Main(masters):
    try:
        import sys
        import win32com.client
        import pyperclip
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

        st = ""
        for master in masters:
            st += f'{master["storage_unit"]}\r\n'
        pyperclip.copy(st)

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nHUMO"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tabsTABSTRIP_ORDER_CRITERIA/tabpTEXT-230/ssub%_SUBSCREEN_ORDER_CRITERIA:RHU_HELP:2010/btn%_SELEXIDV_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[24]").press()
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/tabsTABSTRIP_ORDER_CRITERIA/tabpTEXT-230/ssub%_SUBSCREEN_ORDER_CRITERIA:RHU_HELP:2010/txtNODIS").text = "99999999"
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/tbar[1]/btn[9]").press()
        if len(masters) == 1:
            session.findById("wnd[0]/mbar/menu[2]/menu[0]/menu[4]").select()

    except Exception as e:
        print(e)
        print(sys.exc_info()[0])

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    print(Main([{'storage_unit': '0178010857', 'stock': '72'}]))
    # print(Main([
    #     {'storage_unit': '0177482587', 'stock': '72'},
    #     {'storage_unit': '0177482588', 'stock': '72'},
    #     {'storage_unit': '0177984231', 'stock': '72'},
    #     {'storage_unit': '0177956236', 'stock': '72'},
    #     {'storage_unit': '0177994946', 'stock': '72'},
    #     {'storage_unit': '0177994947', 'stock': '72'},
    #     {'storage_unit': '0177994948', 'stock': '72'},
    #     {'storage_unit': '0177855223', 'stock': '72'},
    #     {'storage_unit': '0177916229', 'stock': '72'},
    #     {'storage_unit': '0169013616', 'stock': '72'},
    #     {'storage_unit': '0177966048', 'stock': '72'},
    #     {'storage_unit': '0177982948', 'stock': '72'},
    #     {'storage_unit': '0172221828', 'stock': '72'},
    #     {'storage_unit': '0172221608', 'stock': '72'},
    #     {'storage_unit': '0170638274', 'stock': '72'},
    #     {'storage_unit': '0170638273', 'stock': '72'},
    #     {'storage_unit': '0170638272', 'stock': '72'},
    #     {'storage_unit': '0170638271', 'stock': '72'},
    #     {'storage_unit': '0170638270', 'stock': '72'},
    #     {'storage_unit': '0170638269', 'stock': '72'},
    #     {'storage_unit': '0170616228', 'stock': '72'},
    #     {'storage_unit': '0170616224', 'stock': '72'},
    #     {'storage_unit': '0177786851', 'stock': '72'},
    #     {'storage_unit': '0177629446', 'stock': '72'},
    #     {'storage_unit': '0177997632', 'stock': '72'},
    #     {'storage_unit': '0177997633', 'stock': '72'},
    #     {'storage_unit': '0177844530', 'stock': '72'},
    #     {'storage_unit': '0177996572', 'stock': '72'},
    #     {'storage_unit': '0177677895', 'stock': '72'},
    #     {'storage_unit': '0177678091', 'stock': '72'},
    #     {'storage_unit': '0177995046', 'stock': '72'},
    #     {'storage_unit': '0177995045', 'stock': '72'},
    #     {'storage_unit': '0177995044', 'stock': '72'},
    #     {'storage_unit': '0177995043', 'stock': '72'},
    #     {'storage_unit': '0177995437', 'stock': '72'},
    #     {'storage_unit': '0177995441', 'stock': '72'},
    #     {'storage_unit': '0178009166', 'stock': '72'},
    #     {'storage_unit': '0178009165', 'stock': '72'},
    #     {'storage_unit': '0178009164', 'stock': '72'},
    #     {'storage_unit': '0178009163', 'stock': '72'},
    #     {'storage_unit': '0178009162', 'stock': '72'},
    #     {'storage_unit': '0178009161', 'stock': '72'},
    #     {'storage_unit': '0178009160', 'stock': '72'},
    #     {'storage_unit': '0178009159', 'stock': '72'},
    #     {'storage_unit': '0178009158', 'stock': '72'},
    #     {'storage_unit': '0178009157', 'stock': '72'},
    #     {'storage_unit': '0178009156', 'stock': '72'},
    #     {'storage_unit': '0178009155', 'stock': '72'},
    #     {'storage_unit': '0178009154', 'stock': '72'},
    #     {'storage_unit': '0178009153', 'stock': '72'},
    #     {'storage_unit': '0178009152', 'stock': '72'},
    #     {'storage_unit': '0178009093', 'stock': '72'},
    #     {'storage_unit': '0178009094', 'stock': '72'},
    #     {'storage_unit': '0178009095', 'stock': '72'},
    #     {'storage_unit': '0178009096', 'stock': '72'},
    #     {'storage_unit': '0178009097', 'stock': '72'},
    #     {'storage_unit': '0178009098', 'stock': '72'},
    #     {'storage_unit': '0178009099', 'stock': '72'},
    #     {'storage_unit': '0178009100', 'stock': '72'},
    #     {'storage_unit': '0178009146', 'stock': '72'},
    #
    # ]))

# -End-------------------------------------------------------------------
