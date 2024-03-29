# -Begin-----------------------------------------------------------------

# -Sub Main--------------------------------------------------------------

def Main(con, storage_type, storage_bin):
    """
    Function checks if storage bin is part of storage type
    """
    import json
    import sys
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
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLS11"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtS1_LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtS1_LGTYP-LOW").text = storage_type
        session.findById("wnd[0]/usr/ctxtS1_LGPLA-LOW").text = storage_bin
        session.findById("wnd[0]/usr/ctxtS1_LGPLA-LOW").setFocus()
        # session.findById("wnd[0]/usr/ctxtS1_LGPLA-LOW").caretPosition = 6
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        # session.findById("wnd[0]/usr/lbl[5,6]").setFocus()
        bin = session.findById("wnd[0]/usr/lbl[5,6]").Text
        # session.findById("wnd[0]/usr/lbl[5,6]").caretPosition = 6
        # session.findById("wnd[0]").sendVKey(2)
        # session.findById("wnd[0]/tbar[0]/btn[15]").press()
        # session.findById("wnd[0]/tbar[0]/btn[15]").press()
        # session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        # session.findById("wnd[0]").sendVKey(0)


        response = {"result": bin, "error": "N/A"}
        return json.dumps(response)

    except:
      session.findById("wnd[0]/tbar[0]/btn[15]").press()
      session.findById("wnd[0]/tbar[0]/btn[15]").press()
      error = session.findById("wnd[0]/sbar/pane[0]").Text
      response = {"result": "N/A", "error": error}
      return json.dumps(response)

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("FG", "ACREDIT TA")

# -End-------------------------------------------------------------------
