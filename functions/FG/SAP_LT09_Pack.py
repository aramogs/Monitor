# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------



# -Sub Main--------------------------------------------------------------
def Main(serial_num_list):
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

        response_list = []
        bin_list = []
        err = False
        for serial_num in serial_num_list:
            session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT09"
            session.findById("wnd[0]").sendVKey(0)
            try:
                session.findById("wnd[0]/usr/txtLEIN-LENUM").text = serial_num
                session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
                session.findById("wnd[0]").sendVKey(0)
                session.findById("wnd[0]/usr/ctxt*LTAP-NLTYP").text = "923"
                session.findById("wnd[0]/usr/txt*LTAP-NLPLA").text = "pack.bin"
                storage_type = session.findById("wnd[0]/usr/ctxt*LTAP-VLTYP").Text
                storage_bin = session.findById("wnd[0]/usr/txt*LTAP-VLPLA").Text
                part_number = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-MATNR[0,0]").Text
                session.findById("wnd[0]/tbar[0]/btn[11]").press()
                result = session.findById("wnd[0]/sbar/pane[0]").Text
                # Getting the values from the source storage type and storage bin for all serial numbers
                bin_list.append({"serial_num": serial_num, "storage_type": storage_type, "storage_bin": storage_bin})
                # Getting only the transfer order and not the text
                response_list.append({"serial_num": serial_num, "result": int(re.sub(r"\D", "", result, 0)), "error":"N/A" })
            except:
                err = True
                result = session.findById("wnd[0]/sbar/pane[0]").Text
                response_list.append({"serial_num": serial_num, "error": f'{result}'})

                session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
                session.findById("wnd[0]").sendVKey(0)
                # response = {"result": "N/A", "error": f'{response_list}', "part_number": "N/A", "bin_list": bin_list}
                # return json.dumps(response)

        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except Exception as e:
            pass

        if err:
            response = {"result": "N/A", "error": f'{response_list}', "part_number": "N/A", "bin_list": f'{bin_list}'}
        else:
            response = {"result": f'{response_list}', "error": "N/A", "part_number": part_number, "bin_list": f'{bin_list}'}


        return json.dumps(response)


    except:
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error, "part_number": "N/A", "bin_list": f'{[]}'}
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
        except:
            pass
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
    Main(["0171689409"])


# -End-------------------------------------------------------------------
