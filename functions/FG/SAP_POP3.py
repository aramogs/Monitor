# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------



# -Sub Main--------------------------------------------------------------
def Main(material_number):
    import sys
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nPOP3"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtPIKP-PIID").text = f'UM{material_number}'
        session.findById("wnd[0]").sendVKey(0)

        session.findById("wnd[0]/usr/tabsTABSTRIP1/tabpTAB3").select()
        try:
            y = 0
            while True:

                packing_material = session.findById(f'wnd[0]/usr/tabsTABSTRIP1/tabpTAB3/ssubSUB1:SAPLVHUPO:0613/tblSAPLVHUPOTC0613/ctxtPIPO_ROW-DETAIL_ITEMTYPE[1,{y}]').Text
                if packing_material =='P':
                   container = session.findById(f'wnd[0]/usr/tabsTABSTRIP1/tabpTAB3/ssubSUB1:SAPLVHUPO:0613/tblSAPLVHUPOTC0613/ctxtPIPO_ROW-COMPONENT[2,{y}]').Text
                   raise Exception()
                y+= 1
        except:
            pass
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        response = {"result": f'{container}', "error": "N/A"}
        return json.dumps(response)
    except:
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
    Main("7000019691Af")

# -End-------------------------------------------------------------------
