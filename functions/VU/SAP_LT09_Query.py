# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------
# -Sub Main--------------------------------------------------------------


def Main(connection_number, serial_num):
    """
    Function used to get the Material Number corresponding the Serial Number
    """

    import json
    import win32com.client
    import pythoncom
    # serial_num = sys.argv[1]
    try:
        pythoncom.CoInitialize()
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
        if not type(SapGuiAuto) == win32com.client.CDispatch:
            return

        application = SapGuiAuto.GetScriptingEngine
        if not type(application) == win32com.client.CDispatch:
            SapGuiAuto = None
            return

        connection = application.Children(connection_number)
        if not type(connection) == win32com.client.CDispatch:
            application = None
            SapGuiAuto = None
            return

        if connection.DisabledByServer == True:
            application = None
            SapGuiAuto = None
            return

        session = connection.Children(0)
        if not type(session) == win32com.client.CDispatch:
            connection = None
            application = None
            SapGuiAuto = None
            return

        if session.Info.IsLowSpeedConnection == True:
            connection = None
            application = None
            SapGuiAuto = None
            return

        # session.findById("wnd[0]").resizeWorkingPane(90, 24, 0)
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT09"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/txtLEIN-LENUM").text = serial_num
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "999"
        # session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").setFocus()
        # session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").caretPosition = 3


        session.findById("wnd[0]").sendVKey(0)



        # session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-MATNR[0,0]").setFocus()
        # session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-MATNR[0,0]").caretPosition = 6
        material_number = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-MATNR[0,0]").Text
        quant = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/txtRL03T-ANFME[1,0]").Text
        material_description = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/txtLTAP-MAKTX[12,0]").Text

        session.findById("wnd[0]/tbar[0]/btn[12]").press()
        session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        session.findById("wnd[0]/tbar[0]/btn[12]").press()
        # Se crea respuesta y se carga en un Json con dumps

        response = {"material_number": material_number,"error": "N/A"}
        return json.dumps(response)
    except:

        if session.Children.Count == 2:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()

        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"material_number": "N/A", "error": error}
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
    Main(123456789)
# -End-------------------------------------------------------------------


