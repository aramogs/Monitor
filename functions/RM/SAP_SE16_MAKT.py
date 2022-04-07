# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------

# -Sub Main--------------------------------------------------------------
def Main(con, material_list):
    import pyperclip
    import json
    import win32com.client
    try:

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

        st = ""
        for material in material_list:
            st += f'{material}\r\n'
        pyperclip.copy(st)

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nSE16"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtDATABROWSE-TABLENAME").text = "MAKT"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/btn%_I1_%_APP_%-VALU_PUSH").press()
        session.findById("wnd[1]/tbar[0]/btn[24]").press()
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        session.findById("wnd[0]/usr/ctxtLIST_BRE").text = "250"
        session.findById("wnd[0]/usr/txtMAX_SEL").text = ""
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        # Crear FOR para encontrar el que se llame SPRAS
        session.findById("wnd[0]/usr/lbl[22,1]").setFocus()
        # Presionar para seleccionar SPRAS
        session.findById("wnd[0]").sendVKey(2)
        session.findById("wnd[0]/tbar[1]/btn[29]").press()
        session.findById("wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").text = "E"
        session.findById("wnd[1]/usr/ssub%_SUBSCREEN_FREESEL:SAPLSSEL:1105/ctxt%%DYN001-LOW").caretPosition = 1
        session.findById("wnd[1]/tbar[0]/btn[0]").press()

        original_position = 0
        maxScroll = session.findById("wnd[0]/usr").verticalScrollbar.Maximum
        try:
            y = 3
            while True:
                q = session.findById(f'wnd[0]/usr/lbl[9,{y}]').Text
                y += 1
                original_position += 1

        except:
            pass
        try:
            info_list = []
            discovered_material = []
            while True:
                y = 3
                for x in range(original_position):
                    discovered_material.append(session.findById(f"wnd[0]/usr/lbl[9,{y}]").Text)
                    q = {
                        "material": session.findById(f"wnd[0]/usr/lbl[9,{y}]").Text,
                        "material_description": session.findById(f"wnd[0]/usr/lbl[28,{y}]").Text
                    }

                    y += 1
                    info_list.append(q)
                if maxScroll != 0:
                    session.findById("wnd[0]/usr").verticalScrollbar.position += original_position
                else:
                    raise Exception("Nothing to do here")

        except Exception as error:
            pass

        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)

        not_found_material = list(set(material_list) - set(discovered_material))

        if len(not_found_material) > 0:
            response = {"result": "N/A", "error": not_found_material}
        else:
            response = {"result": info_list, "error": "N/A"}
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
    Main([
            "1000009293A0",
            "1000009295A0",
            "1000009307A0",
            "1000009350A0",
            "1000009352A0",
            "1000009354A0",
            "1000009356A0",
            "1000009358A0",
            "1000009360A0",
            "1000009362A0",
            "1000009364A0",
            "1000009404A0",
            "1000009406A0",
            "1000009417A0",
            "1000009420A0",
            "1000009449A0",
            "1000009451A0",
            "1000009453A0",
            "1000009455A0",
            "1000009457A0",
            "1000009464A0",
            "1000009486A0",
            "1000009488A0",
            "1000009491A0",
            "1000009493A0",
            "1000009496A0",
            "1000009498A0",
            "1000009513A0",
            "1000009517A0",
            "1000009519A0",
            "1000009521A0",
            "1000009523A0",
            "1000009525A0",
            "1000009527A0",
            "1000009530A0",
            "1000009532A0",
            "1000009534A0",
            "1000009536A0",
            "1000009538A0",
            "1000009540A0",
            "1000009543A0",
            "1000009545A0",
            "1000009547A0",
            "1000009549A0",
            "1000009552A0",
            "1000009554A0",
            "1000009556A0",
            "1000009558A0",
            "1000009560A0",
            "1000009562A0"
          ])
# -End-------------------------------------------------------------------
