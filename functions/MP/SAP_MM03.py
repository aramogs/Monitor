# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------



def Main(material):
    # material = sys.argv[1]
    import sys
    import win32com.client
    import json
    import pythoncom
    try:
        pythoncom.CoInitialize()
        SapGuiAuto = win32com.client.GetObject("SAPGUI")

        application = SapGuiAuto.GetScriptingEngine

        connection = application.Children(0)

        if connection.DisabledByServer == True:
            # print("Scripting is disabled by server")
            application = None
            SapGuiAuto = None
            return

        session = connection.Children(0)

        if session.Info.IsLowSpeedConnection == True:
            # print("Connection is low speed")
            connection = None
            application = None
            SapGuiAuto = None
            return

        # session.findById("wnd[0]").resizeWorkingPane(83, 38, 0)
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nMM03"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtRMMG1-MATNR").text = material
        session.findById("wnd[0]").sendVKey(0)
        # session.findById("wnd[0]/tbar[1]/btn[5]").press()
        # session.findById("wnd[1]/tbar[0]/btn[19]").press()
        # session.findById("wnd[1]/usr/tblSAPLMGMMTC_VIEW").getAbsoluteRow(0).selected = -1
        # session.findById("wnd[1]/tbar[0]/btn[0]").press()
        net_weight = session.findById(
            "wnd[0]/usr/tabsTABSPR1/tabpSP01/ssubTABFRA1:SAPLMGMM:2004/subSUB5:SAPLMGD1:2007/txtMARA-NTGEW").Text

        session.findById("wnd[0]/tbar[0]/btn[15]").press()

        response = {"net_weight": net_weight}
        return (json.dumps(response))

    except:
        return (sys.exc_info()[0])

    finally:
        session = None
        connection = None
        application = None
        SapGuiAuto = None


# -Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("1000009356A0")

# -End-------------------------------------------------------------------
