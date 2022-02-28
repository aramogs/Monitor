# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(sap_num, quant):
    """
    Function takes a material number and quantity to perform transfer order
    The transfer order is from 102/103 to VUL/V02
    """
    import json
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT01"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtLTAK-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "100"
        session.findById("wnd[0]/usr/ctxtLTAP-MATNR").text = sap_num
        session.findById("wnd[0]/usr/txtRL03T-ANFME").text = quant
        session.findById("wnd[0]/usr/ctxtLTAP-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtLTAP-LGORT").text = "0012"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/usr/ctxtLTAP-LETYP").text = "IP"
        session.findById("wnd[0]/usr/ctxtLTAP-VLTYP").text = "102"
        session.findById("wnd[0]/usr/ctxtLTAP-VLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-VLPLA").text = "103"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]/usr/ctxtLTAK-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "199"
        session.findById("wnd[0]/usr/ctxtLTAP-MATNR").text = sap_num
        session.findById("wnd[0]/usr/txtRL03T-ANFME").text = quant
        session.findById("wnd[0]/usr/ctxtLTAP-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtLTAP-LGORT").text = "0012"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/usr/ctxtLTAP-LETYP").text = "IP"
        session.findById("wnd[0]/usr/ctxtLTAP-LDEST").text = "dummy"
        session.findById("wnd[0]/usr/ctxtLTAP-NLTYP").text = "VUL"
        session.findById("wnd[0]/usr/ctxtLTAP-NLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-NLPLA").text = "V02"
        session.findById("wnd[0]").sendVKey(0)
        serial_num = session.findById("wnd[0]/usr/ctxtLTAP-NLENR").Text
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[0]/btn[11]").press()

        result = session.findById("wnd[0]/sbar/pane[0]").Text
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass
        response = {"serial": serial_num, "result": f'{result}', "error": "N/A"}

        return json.dumps(response)

    except:
        try:
           error = session.findById("wnd[1]/usr/txtSPOP-TEXTLINE1").Text
           session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
           session.findById("wnd[0]/tbar[0]/btn[12]").press()
           session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        except:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"serial": "N/A", "result": "N/A", "error": error}

        # session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
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
    Main("5000010050A0","6")

# -End-------------------------------------------------------------------
