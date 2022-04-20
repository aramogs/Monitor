# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------
# -Sub Main--------------------------------------------------------------


def Main(connection_number, serial_num_list, storage_type, storage_bin, station):
    """
    Function used to get the Material Number corresponding the Serial Number
    """

    import json
    import win32com.client
    import pythoncom
    import functions.DB.Functions
    import re
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

        response_list = []
        count = 0

        for serial_num in serial_num_list:
            session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT09"
            session.findById("wnd[0]").sendVKey(0)
            session.findById("wnd[0]/usr/txtLEIN-LENUM").text = serial_num
            session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"

            session.findById("wnd[0]").sendVKey(0)

            try:
                text = session.findById("wnd[0]/sbar/pane[0]").Text
                if text == "":
                    sap_num = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-MATNR[0,0]").Text
                    sap_description = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/txtLTAP-MAKTX[12,0]").Text
                    session.findById("wnd[0]/usr/ctxt*LTAP-NLTYP").text = storage_type
                    session.findById("wnd[0]/usr/txt*LTAP-NLPLA").text = storage_bin
                    session.findById("wnd[0]/tbar[0]/btn[11]").press()
                    result = session.findById("wnd[0]/sbar/pane[0]").Text
                    raise Exception(result)
                else:
                    response_list.append({"result": "OK", "serial": f'{serial_num}', "sap_num": "N/A", "sap_description": "N/A", "error": "N/A"})
            except Exception as e:
                response_list.append({"result": "N/A", "serial": f'{serial_num}', "sap_num": f'{sap_num}', "sap_description": f'{sap_description}', "error": f'{e}'})

            try:
                if count == 0:
                    functions.DB.Functions.DBR.set_hash(re.sub(":", "-", station), serial_num)
                else:
                    functions.DB.Functions.DBR.update_hash(re.sub(":", "-", station), serial_num)

                # DB.Functions.DBR.get_hash(station_hash)
            except Exception as e:
                print(e)
            count += 1

        response = {"result": f'{response_list}', "error": "N/A"}

        return json.dumps(response)

    except Exception as err:
        if session.Children.Count == 2:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()

        return json.dumps({"result": "N/A", "error": f'{err}'})


    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    print(Main(0, ["1032560990", "1033010532", "0179383074", "1032560954"], 102, 103, "00-00-00-00-00-00"))
# -End-------------------------------------------------------------------


