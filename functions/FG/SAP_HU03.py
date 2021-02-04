# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(serials):
    import sys
    import json
    import win32com.client
    import subprocess
    try:

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
        # DO NOT COMMENT
        # THIS IS NECESSARY IN ORDER TO GET THE BIGGEST AMOUNT OF INFORMATION AT THE SAME TIME
        session.findById("wnd[0]").resizeWorkingPane(80, 38, 0)
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nHU03"
        session.findById("wnd[0]").sendVKey(0)
        x = 0
        y = 0
        container_list = []
        if len(serials) > 1:
            for serial in serials:
                session.findById(f'wnd[0]/usr/tblRHU_DISPLAY_HANDLING_UNITSTC_HU_ANZ/ctxtVEKP-EXIDV[0,{x}]').text = serial
                x+=1
            session.findById("wnd[0]/tbar[1]/btn[8]").press()

            session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS").select()

            for serial in serials:
                if y < 14:
                    serial_ = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-EXIDV[0,{y}]').Text
                    container_ = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-VHILM[1,{y}]').Text
                    container_list.append({"serial": serial_, "container": container_})
                else:
                    y = 13

                    session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003").verticalScrollbar.position = 1
                    serial_ = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-EXIDV[0,{y}]').Text
                    container_ = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-VHILM[1,{y}]').Text
                    container_list.append({"serial": serial_, "container": container_})
                y += 1

            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)

        else:
            session.findById(f'wnd[0]/usr/tblRHU_DISPLAY_HANDLING_UNITSTC_HU_ANZ/ctxtVEKP-EXIDV[0,{x}]').text = serials[0]
            session.findById("wnd[0]/tbar[1]/btn[8]").press()
            session.findById("wnd[0]/tbar[0]/btn[3]").press()
            session.findById("wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS").select()
            serial_ = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-EXIDV[0,0]').Text
            container_ = session.findById(f'wnd[0]/usr/tabsTS_HU_VERP/tabpUE6HUS/ssubTAB:SAPLV51G:6020/tblSAPLV51GTC_HU_003/ctxtV51VE-VHILM[1,0]').Text

            container_list.append({"serial": serial_, "container": container_})
            session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
            session.findById("wnd[0]").sendVKey(0)

        response = {"result": f'{container_list}', "error": "N/A"}
        print(response)
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
    # Main(["171688969", "171688970", "171689042", "171t689043", "171689046", "171689047", "171689048", "171689049",
    #       "171689050", "171689051", "170518182", "171688592", "170938261", "168250646", "168250632", "168250635","171558480"])
    Main(["171689403", "171689404", "171689405","171689406","171689407","171689408","171689409","171689410","171689411","171689412","171689413","171689414","171689415"
         ,"171689416","171689417","171689418","171689419","171689420","171689421","171689422","171689423","171689424", "171689425", "171689426","171689427","171689428"
          ,"171689429","171689430","171689431","171689432","171689433","171689434","171689435","171689436","171689437","171689438","171689439","171689440","171689441","171689442"])

# -End-------------------------------------------------------------------
