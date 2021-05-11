# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(sap_num, quant, source_bin, destination_bin):
    """
    Function takes a material number and quantity to perform transfer order
    The transfer order is from 102/103 to VUL/V02
    """
    import json
    import re
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
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
        session.findById("wnd[0]/usr/ctxtLTAP-MATNR").text = sap_num
        session.findById("wnd[0]/usr/txtRL03T-ANFME").text = quant
        session.findById("wnd[0]/usr/ctxtLTAP-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtLTAP-LGORT").text = "0012"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/usr/ctxtLTAP-LDEST").text = "dummy"
        session.findById("wnd[0]/usr/ctxtLTAP-VLTYP").text = "102"
        session.findById("wnd[0]/usr/ctxtLTAP-VLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-VLPLA").text = source_bin
        session.findById("wnd[0]/usr/ctxtLTAP-NLTYP").text = "102"
        session.findById("wnd[0]/usr/ctxtLTAP-NLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-NLPLA").text = destination_bin
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)
        result = session.findById("wnd[0]/sbar/pane[0]").Text
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        print(re.sub(r"\D", "", result, 0))
        if re.sub(r"\D", "", result, 0) != "":
            response = {"result": int(re.sub(r"\D", "", result, 0)), "error": "N/A"}
        else:
            response = {"result": "N/A", "error": result}

        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass

        return json.dumps(response)

    except:
        try:
            error = session.findById("wnd[1]/usr/txtSPOP-TEXTLINE1").Text
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
            session.findById("wnd[0]/tbar[0]/btn[12]").press()
            session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        except:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

        # session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
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
    Main("5000010050A0", "6")

# -End-------------------------------------------------------------------
