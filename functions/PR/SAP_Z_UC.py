# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(printer):
    import sys
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nZ_UC"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtV_DISPO").text = "001"
        session.findById("wnd[0]/usr/ctxtB_DISPO").text = "999"
        session.findById("wnd[0]/usr/ctxtP_LDEST").text = printer
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)


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
    Main("dummy")
# -End-------------------------------------------------------------------
