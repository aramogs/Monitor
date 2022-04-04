# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------



def Main(material_list):
    """
    Function gets material number and returns the net weight
    """
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
        session.findById("wnd[0]/tbar[0]/okcd").text = "/nMM03"
        session.findById("wnd[0]").sendVKey(0)
        for material in material_list:
            session.findById("wnd[0]/usr/ctxtRMMG1-MATNR").text = material
            session.findById("wnd[0]").sendVKey(0)
            material_description = session.findById("wnd[0]/usr/tabsTABSPR1/tabpSP01/ssubTABFRA1:SAPLMGMM:2004/subSUB1:SAPLMGD1:1002/txtMAKT-MAKTX").Text
            session.findById("wnd[0]/tbar[0]/btn[3]").press()

            response = {"material_description": material_description}
            # print(response)
        return json.dumps(response)

    except:
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        session.findById("wnd[0]/tbar[0]/btn[15]").press()
        error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"result": "N/A", "error": error}
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
"1000009562A0",
"1000009564A0",
"1000009567A0",
"1000009571A0",
"1000009573A0",
"1000009575A0",
"1000009577A0",
"1000009580A0",
"1000009584A0",
"1000009588A0",
"1000009590A0",
"1000009604A0",
"1000009610A0",
"1000009612A0",
"1000009614A0",
"1000009616A0",
"1000009618A0",
"1000009620A0",
"1000009622A0",
"1000009624A0",
"1000009626A0",
"1000009631A0",
"1000009634A0",
"1000009636A0",
"1000009638A0",
"1000009659A0",
"1000009661A0",
"1000009663A0",
"1000009665A0",
"1000009667A0",
"1000009669A0"
          ])

# -End-------------------------------------------------------------------
