# -Sub Main--------------------------------------------------------------
def Main(serials):
    try:
        import sys
        import win32com.client
        import pyperclip
        import json
        import datetime

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

        st = ""
        for serial in serials:
            st += f'{serial}\r\n'
        pyperclip.copy(st)

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nhumo"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tabsTABSTRIP_ORDER_CRITERIA/tabpTEXT-230/ssub%_SUBSCREEN_ORDER_CRITERIA:RHU_HELP:2010/btn%_SELEXIDV_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[24]").press()
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/tabsTABSTRIP_ORDER_CRITERIA/tabpTEXT-230/ssub%_SUBSCREEN_ORDER_CRITERIA:RHU_HELP:2010/radLGRID").select()
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").pressToolbarContextButton("&MB_VARIANT")
        session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").selectContextMenuItem("&LOAD")
        row = 0
        try:
            while 1 > 0:
                if session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").GetCellValue(row, "VARIANT") == "DEL":
                    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").currentCellRow = row
                    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").selectedRows = row
                    session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").clickCurrentCell()
                    raise Exception()
                row += 1
        except Exception as e:
            # print(e)
            pass

        # session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").currentCellRow = 10
        # session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").selectedRows = "10"
        # session.findById("wnd[1]/usr/ssubD0500_SUBSCREEN:SAPLSLVC_DIALOG:0501/cntlG51_CONTAINER/shellcont/shell").clickCurrentCell()
        x = 0
        y = 0
        response_list = []
        master_error = []
        quantity_check = ""
        part_number = ""
        container = ""
        lower_gr_date = datetime.datetime.strptime("01/01/3000", "%m/%d/%Y").date()
        try:
            for serial in serials:
                serial_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "EXIDV")
                container_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "VHILM")
                part_number_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "CML_PACKGOOD")
                gr_date_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "ERDAT")
                packing_object_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "VPOBJ")
                # weight_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "BRGEW")
                # content_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "INHALT")
                quantity_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "CMLQTY_A")
                master_ = session.findById("wnd[0]/usr/cntlCONTAINER_2000/shellcont/shell").GetCellValue(x, "EXIDV2")

                if datetime.datetime.strptime(f'{gr_date_}', "%m/%d/%Y").date() <= lower_gr_date:
                    lower_gr_date = datetime.datetime.strptime(f'{gr_date_}', "%m/%d/%Y").date()

                if x == 0:
                    quantity_check = quantity_
                    part_number = part_number_
                    container = container_

                if quantity_ != quantity_check:
                    response_list.append({"serial_num": serial_, "part_number": part_number_, "gr_date": gr_date_, "error": "Different Quantity Selected"})

                if part_number_ != part_number:
                    response_list.append({"serial_num": serial_, "part_number": part_number_, "gr_date": gr_date_, "error": "Different Part Number Selected"})

                if container_ != container:
                    response_list.append({"serial_num": serial_, "part_number": part_number_, "gr_date": gr_date_, "error": "Different Container Selected"})

                if packing_object_ == "07":
                    # Packing Object
                    #   00 Not Assigned to an Object
                    #   01 Outbound Delivery
                    #   02 Sales Document
                    #   03 Inbound Delivery
                    #   04 Shipment
                    #   05 Non-Assigned Handling Unit
                    #   06 Non-Assigned Handling Unit
                    #   07 Repetitive Manufacturing
                    #   08 Work Order for Components
                    #   09 Work Order - Finished Product
                    #   12 Non-Assigned Handling Unit
                    #   21 Cross-Outbound Delivery
                    #   23 Cross-Inbound Delivery
                    response_list.append({"serial_num": serial_, "part_number": part_number_, "gr_date": gr_date_, "error": "Handling Unit Not BackFlushed"})
                if master_ == "P":
                    master_error.append({"serial_num": serial_, "part_number": part_number_, "gr_date": gr_date_, "error": "Master Unit Selected"})

                response_list.append({"serial_num": serial_, "part_number": part_number_, "gr_date": gr_date_, "error": "N/A"})
                x += 1

        except:
            if len(serials) != len(response_list):
                session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
                session.findById("wnd[0]").sendVKey(0)
                return json.dumps({"result": f'N/A', "error": f'{master_error}'})

        if len(master_error) != 0:
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
            return json.dumps({"result": f'N/A', "error": f'{master_error}'})

        for response in response_list:
            if response["error"] != "N/A":
                return json.dumps({"result": f'N/A', "error": f'{response_list}'})

        # Verifying that the dates are in range of 30 days
        for serial in response_list:
            if lower_gr_date <= datetime.datetime.strptime(f'{serial["gr_date"]}', "%m/%d/%Y").date() <= lower_gr_date + datetime.timedelta(days=30):
                pass
            else:
                return json.dumps({"serial": "N/A", "error": f'{" Verify Handling Units - Dates not in range of 30 days"}'})
            y += 1


        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)
        response = {"result": f'{response_list}', "error": "N/A", "lower_gr_date": f'{lower_gr_date}', "part_number": part_number, "single_container": container}

        return json.dumps(response)

    except Exception as e:
        print(e)

        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)
        # print(response)
        return json.dumps(response)

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------

if __name__ == '__main__':
    Main(["171689403", "171689404", "171689405", "171689406", "171689407", "171689408", "171689409", "171689410", "171689411", "171689412", "171689413", "171689414", "171689415"
         ,"171689416", "171689417", "171689418", "171689419", "171689420", "171689421", "171689422", "171689423", "171689424", "171689425", "171689426", "171689427","171689428"
         ,"171689429", "171689430", "171689431", "171689432", "171689433", "171689434", "171689435", "171689436", "171689437", "171689438", "171689439", "171689440",
          "171689441", "171689442"])
    # Main(["171689403", "171689404", "171689405"])

# -End-------------------------------------------------------------------
