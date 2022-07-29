# -Begin-----------------------------------------------------------------

# -Sub Main--------------------------------------------------------------

def Main(con, serial_num_list, storage_type, storage_bin):
    """
    Function takes a list of storage units and transfers them to the storage type nad bin selected
    """
    import json
    import re
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



        response_list = []
        count = 0
        for serial_num in serial_num_list:

            session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT09"
            session.findById("wnd[0]").sendVKey(0)
            try:
                session.findById("wnd[0]/usr/txtLEIN-LENUM").text = f'{serial_num}'
                session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
                session.findById("wnd[0]").sendVKey(0)
                session.findById("wnd[0]/usr/ctxt*LTAP-NLTYP").text = storage_type
                session.findById("wnd[0]/usr/txt*LTAP-NLPLA").text = storage_bin
                certificate_number = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/txtLTAP-ZEUGN[8,0]").Text
                material = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-MATNR[0,0]").Text
                material_description = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/txtLTAP-MAKTX[12,0]").Text
                quantity = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/txtRL03T-ANFME[1,0]").Text
                session.findById("wnd[0]/tbar[0]/btn[11]").press()
                result = session.findById("wnd[0]/sbar/pane[0]").Text
                # Getting only the transfer order and not the text
                response_list.append({"serial_num": serial_num, "result": int(re.sub(r"\D", "", result, 0)), "certificate_number": certificate_number,
                                      "material": material, "material_description": material_description, "quantity": quantity.replace(".000", "").replace(",", "")})

            except:
                result = session.findById("wnd[0]/sbar/pane[0]").Text
                response_list.append({"serial_num": serial_num, "result": result, "certificate_number": "N/A",
                                      "material": "N/A", "material_description": "N/A", "quantity": "N/A"})

                session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
                session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass
        response = {"result": f'{response_list}', "error": "N/A"}

        return json.dumps(response)


    except:
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"serial_num": "N/A", "result": "N/A", "error": error, "certificate_number": "N/A",
                    "material": "N/A", "material_description": "N/A", "quantity": "N/A"}

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
    Main("0171349693", "MP1", "P0501")

# -End-------------------------------------------------------------------
