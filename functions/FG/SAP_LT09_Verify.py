# -Begin-----------------------------------------------------------------

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
        quantity_check = []
        err = False
        for serial_num in serial_num_list:
            session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT09"
            session.findById("wnd[0]").sendVKey(0)
            session.findById("wnd[0]/usr/txtLEIN-LENUM").text = serial_num
            session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
            session.findById("wnd[0]").sendVKey(0)

            error = session.findById("wnd[0]/sbar/pane[0]").Text
            if error == "":
                error = "N/A"
                part_number = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-MATNR[0,0]").Text
                gr_date = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/ctxtLTAP-WDATU[4,0]").Text
                quantity = session.findById("wnd[0]/usr/subD0171_S:SAPML03T:1711/tblSAPML03TD1711/txtRL03T-ANFME[1,0]").Text
                response_list.append({"serial_num": serial_num, "part_number": part_number, "gr_date": gr_date,"error": error})
                quantity_check.append(quantity) if quantity not in quantity_check else quantity_check
                if len(quantity_check) > 1:
                    return json.dumps({"result": "N/A", "error": "Handling Units with different quantitys,Verify your entries"})
            else:
                err = True
                response_list.append({"serial_num": serial_num, "part_number": "N/A", "gr_date": "N/A", "error": error})


        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        try:
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
        except:
            pass

        if err:
            response = {"result": f'N/A', "error": f'{response_list}'}
        else:
            response = {"result": f'{response_list}', "error": "N/A"}

        return json.dumps(response)


    except:
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

        session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
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
    Main(['0170518182', '0546645645'])
# -End-------------------------------------------------------------------
