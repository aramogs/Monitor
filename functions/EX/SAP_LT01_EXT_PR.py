# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(con, storage_location, sap_num, quantity, from_sbin, to_stype, to_sbin):
    """
    Function takes a material number and quantity to perform transfer order
    The transfer order is from 102/103 to VUL/V02

    Args:
        con: SAP connection number
        storage_location: Storage Location of current building
        sap_num: SAP number (Storage Unit)
        quantity: Quantity to transfer
        from_sbin: Bin to transfer from
        to_sbin:  Bin to transfer to

    Returns:
        Str: Return Json String
    """
    import json
    import win32com.client
    import pythoncom
    try:

        pythoncom.CoInitialize()
        sap_gui_auto = win32com.client.GetObject("SAPGUI")
        application = sap_gui_auto.GetScriptingEngine
        connection = application.Children(con)

        if connection.DisabledByServer:
            print("Scripting is disabled by server")
            application = None
            sap_gui_auto = None
            return json.dumps({"serial": "N/A", "result": "N/A", "error": "Scripting is disabled by server"})

        session = connection.Children(0)

        if session.Info.IsLowSpeedConnection:
            print("Connection is low speed")
            connection = None
            application = None
            sap_gui_auto = None
            return json.dumps({"serial": "N/A", "result": "N/A", "error": "Connection is low speed"})

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT01"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtLTAK-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "100"
        session.findById("wnd[0]/usr/ctxtLTAP-MATNR").text = sap_num
        session.findById("wnd[0]/usr/txtRL03T-ANFME").text = quantity
        session.findById("wnd[0]/usr/ctxtLTAP-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtLTAP-LGORT").text = storage_location
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/usr/ctxtLTAP-LETYP").text = "IP"
        session.findById("wnd[0]/usr/ctxtLTAP-VLTYP").text = "102"
        session.findById("wnd[0]/usr/ctxtLTAP-VLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-VLPLA").text = from_sbin
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        session.findById("wnd[0]/usr/ctxtLTAK-LGNUM").text = "521"
        session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "199"
        session.findById("wnd[0]/usr/ctxtLTAP-MATNR").text = sap_num
        session.findById("wnd[0]/usr/txtRL03T-ANFME").text = quantity
        session.findById("wnd[0]/usr/ctxtLTAP-WERKS").text = "5210"
        session.findById("wnd[0]/usr/ctxtLTAP-LGORT").text = storage_location
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[1]/btn[5]").press()
        session.findById("wnd[0]/usr/ctxtLTAP-LETYP").text = "IP"
        session.findById("wnd[0]/usr/ctxtLTAP-LDEST").text = "dummy"
        session.findById("wnd[0]/usr/ctxtLTAP-NLTYP").text = to_stype
        session.findById("wnd[0]/usr/ctxtLTAP-NLBER").text = "001"
        session.findById("wnd[0]/usr/txtLTAP-NLPLA").text = to_sbin
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
        sap_gui_auto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("0", "5000010050A0", "6", 5, "102", "102")

# -End-------------------------------------------------------------------
