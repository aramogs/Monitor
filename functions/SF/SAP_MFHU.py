# -Begin-----------------------------------------------------------------

# -Includes--------------------------------------------------------------


# -Sub Main--------------------------------------------------------------
def Main(serial_num):
    """
    Function takes a serial number and performs a backflush
    If everything is right the function returns no errors
    """
    import win32com.client
    import json
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

        session.findById("wnd[0]/tbar[0]/okcd").text = "/nMFHU"
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]/usr/ctxtVHURMEAE-EXIDV_I").text = serial_num
        session.findById("wnd[0]/usr/ctxtVHURMEAE-WERKS").text = "5210"
        session.findById("wnd[0]/usr/txtVHURMEAE-VERID").text = "1"
        # session.findById("wnd[0]/usr/txtVHURMEAE-VERID").setFocus()
        # session.findById("wnd[0]/usr/txtVHURMEAE-VERID").caretPosition = 1
        session.findById("wnd[0]").sendVKey(0)

        try:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
            if error != "":
                session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
                session.findById("wnd[0]").sendVKey(0)
                response = {"serial_num": serial_num, "result": "N/A", "error": error}
                return json.dumps(response)
            else:
                raise Exception()
        except:
            pass
        session.findById("wnd[0]/tbar[0]/btn[11]").press()
        try:
            error = session.findById("wnd[0]/sbar").Text
            if error != "Handling unit backflush completed":
                response = {"serial_num": serial_num, "result": "N/A", "error": error}
                session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
                session.findById("wnd[0]").sendVKey(0)
                return json.dumps(response)
            else:
                raise Exception()
        except:
            session.findById("wnd[0]").sendVKey(5)
            session.findById("wnd[0]/tbar[1]/btn[94]").press()
        try:
            messages = []
            y = 5
            while 1 > 0:
                message = session.findById(f'wnd[0]/usr/lbl[27,{y}]').Text
                y += 1
                messages.append(message)
        except:
            pass
        session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
        session.findById("wnd[0]").sendVKey(0)


        if "not" in messages[0]:
            #messages.pop(0)
            error = messages
            print(messages)
        else:
            error = "N/A"

        response = {"serial_num": serial_num, "result": "N/A", "error": error}
        return json.dumps(response)
    except:
        try:
            error = session.findById("wnd[1]/usr/txtSPOP-TEXTLINE1").Text
            session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
            session.findById("wnd[0]/tbar[0]/btn[12]").press()
            session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        except:
            error = session.findById("wnd[0]/sbar/pane[0]").Text
        response = {"serial_num": "N/A", "result": "N/A", "error": error}

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
    Main("171688435")
# -End-------------------------------------------------------------------
