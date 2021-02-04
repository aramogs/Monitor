# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(sap_num, quanity, from_Stype, from_S_bin, to_Stype, to_Sbin):
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
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
        session.findById("wnd[0]/usr/ctxtLTAP-MATNR").text = sap_num
        session.findById("wnd[0]/usr/txtRL03T-ANFME").text = quanity
        session.findById("wnd[0]/usr/ctxtLTAP-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtLTAP-LGORT").text = "0012"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtLTAP-LDEST").text = "dummy"
        session.findById("wnd[0]/usr/ctxtLTAP-VLTYP").text = from_Stype
        session.findById("wnd[0]/usr/ctxtLTAP-VLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-VLPLA").text = from_S_bin
        session.findById("wnd[0]/usr/ctxtLTAP-NLTYP").text = to_Stype
        session.findById("wnd[0]/usr/ctxtLTAP-NLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-NLPLA").text = to_Sbin
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)


        result = session.findById("wnd[0]/sbar/pane[0]").Text

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass
        response = {"serial": "N/A", "result": f'{result}', "error": "N/A"}
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

        return (json.dumps(response))

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("5V0005305195", "10000", "102", "RETRABAJO", "102", "103")

# -End-------------------------------------------------------------------
