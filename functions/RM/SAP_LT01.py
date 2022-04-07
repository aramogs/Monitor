# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------

# -Sub Main--------------------------------------------------------------
# material = sys.argv[1]
# cantidad = sys.argv[2]
# serial_num = sys.argv[3]


def Main(con, material, quantity, serial_num):
    """
    Function takes material number, quantity and serial number
    Then gets the serial number and withdraws the quantity from the serial number
    """
    import sys
    import win32com.client
    import json
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

        # session.findById("wnd[0]").resizeWorkingPane(118, 38, 0)
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT01"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtLTAK-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
        session.findById("wnd[0]/usr/ctxtLTAP-MATNR").text = material
        session.findById("wnd[0]/usr/txtRL03T-ANFME").text = quantity
        # session.findById("wnd[0]/usr/ctxtLTAP-ALTME").text = "PC"
        session.findById("wnd[0]/usr/ctxtLTAP-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtLTAP-LGORT").text = "0011"
        # session.findById("wnd[0]/usr/ctxtLTAP-LGORT").setFocus()
        # session.findById("wnd[0]/usr/ctxtLTAP-LGORT").caretPosition = 4
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtLTAP-VLTYP").text = "MP"
        session.findById("wnd[0]/usr/ctxtLTAP-VLBER").text = "001"
        session.findById("wnd[0]/usr/ctxtLTAP-VLENR").text = serial_num
        session.findById("wnd[0]/usr/ctxtLTAP-NLTYP").text = "102"
        session.findById("wnd[0]/usr/ctxtLTAP-NLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-NLPLA").text = "104"
        # session.findById("wnd[0]/usr/txtLTAP-NLPLA").setFocus()
        # session.findById("wnd[0]/usr/txtLTAP-NLPLA").caretPosition = 3
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)

        result = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": result, "error": "N/A"}

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        return (json.dumps(response))

    except:
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        return (json.dumps(response))

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main()

# -End-------------------------------------------------------------------
