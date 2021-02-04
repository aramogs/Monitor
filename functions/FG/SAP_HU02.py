# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(container, part_number, client_part_number, serials):
    import json
    import sys
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
        weight = 0
        session.findById("wnd[0]").resizeWorkingPane(80, 38, 0)
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nHU02"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS").select()
        session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-VHILM[1,0]").text = container
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]").sendVKey(2)
        session.findById("wnd[0]/usr/tabsTS_HU_DET/tabpDETZUS").select()
        session.findById("wnd[0]/usr/tabsTS_HU_DET/tabpDETZUS/ssubTAB:SAPLV51G:6130/ctxtVEKPVB-PACKVORSCHR").text = f'UM{part_number}'
        # session.findById("wnd[0]/usr/tabsTS_HU_DET/tabpDETZUS/ssubTAB:SAPLV51G:6130/ctxtVEKPVB-PACKVORSCHR").setFocus()
        session.findById("wnd[0]/usr/tabsTS_HU_DET/tabpDETVERTR").select()
        session.findById("wnd[0]/usr/tabsTS_HU_DET/tabpDETVERTR/ssubTAB:SAPLV51G:6150/txtVEKPVB-INHALT").text = client_part_number
        session.findById("wnd[0]/usr/txtVEKP-EXIDV2").text = "P"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/tbar[0]/btn[3]").press()

        master = session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-EXIDV[0,0]").Text
        w = session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/txtV51VE-BRGEW[3,0]").Text
        weight += float(w)
        x = 1
        scroll = 1
        scroll2 = 1

        for serial in serials:
            try:
                if x < 13:
                    session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-EXIDV[0,{x}]').text = serial
                else:
                    session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003").verticalScrollbar.position = scroll
                    session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-EXIDV[0,{12}]').text = serial
                    scroll += 1
                    pass
                session.findById("wnd[0]").sendVKey(0)
                single_container = session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-VHILM[1,0]").Text

                w = session.findById(
                    "wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/txtV51VE-BRGEW[3,0]").Text
                weight += float(w)
                x += 1

            except Exception as e:
                print(e)
                pass

        session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6POS").select()
        total_quantity = session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6POS/ssubTAB:SAPLV51G:6010/tblSAPLV51GTC_HU_002/txtV51VP-LFIMG[2,0]").Text
        session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS").select()

        session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003").getAbsoluteRow(x - 1).selected = -1
        for y in range(x - 1):
            if y < 15:
                session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_004').getAbsoluteRow(y).selected = -1
            else:
                session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_004").verticalScrollbar.position = scroll2
                session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_004').getAbsoluteRow(y).selected = -1
                scroll2 += 1

        session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/btn%#AUTOTEXT004").press()

        try:
            message = session.findById("wnd[1]/usr/txtMESSTXT1").Text
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)
            return json.dumps({"result": "N/A", "error": message})
        except:
            pass

        try:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
            if error != "Handling unit was packed":
                session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
                session.findById("wnd[0]").sendVKey(0)
                return json.dumps({"result": "N/A", "error": error})
            else:
                pass
        except:
            pass

        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        response = {"result": f'0{master}', "gross_weigth": round(weight, 2), "total_quantity": total_quantity,
                    "single_container": single_container, "error": "N/A"}
        return json.dumps(response)
    except Exception as e:
        # print(e)
        # print(sys.exc_info()[0])

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
    Main("4MP0055","7000019691A0", ["171689403", "171689404", "171689405","171689406","171689407","171689408","171689409","171689410","171689411","171689412","171689413","171689414","171689415"
                     ,"171689416","171689417","171689418","171689419","171689420","171689421","171689422","171689423"])
# -End-------------------------------------------------------------------
