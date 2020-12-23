
#-Begin-----------------------------------------------------------------

#-Includes--------------------------------------------------------------


#-Sub Main--------------------------------------------------------------
def Main(serial_num):
  """
  The function takes a serial number to perform a transfer order
  The transfer is from Vul/??? to 102/103
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

    session.findById("wnd[0]/tbar[0]/okcd").text = "/nLT09"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/txtLEIN-LENUM").text = serial_num
    session.findById("wnd[0]/usr/ctxtLTAK-BWLVS").text = "998"
    session.findById("wnd[0]").sendVKey(0)
    session.findById("wnd[0]/usr/ctxt*LTAP-NLTYP").text = "102"
    session.findById("wnd[0]/usr/ctxt*LTAP-NLBER").text = "001"
    session.findById("wnd[0]/usr/txt*LTAP-NLPLA").text = "103"
    session.findById("wnd[0]/tbar[0]/btn[11]").press()
    result = session.findById("wnd[0]/sbar/pane[0]").Text
    try:
        session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
    except:
        pass
    response = {"result": f'{result}', "error": "N/A"}

    return json.dumps(response)

  except:

      error = session.findById("wnd[0]/sbar/pane[0]").Text
      response = {"result": "N/A", "error": error}

      # session.findById("wnd[1]/usr/btnSPOP-OPTION2").press()
      session.findById("wnd[0]/tbar[0]/okcd").text = "/n"
      session.findById("wnd[0]").sendVKey(0)

      return (json.dumps(response))

  finally:
    session = None
    connection = None
    application = None
    SapGuiAuto = None

#-Main------------------------------------------------------------------
if __name__ == '__main__':
    Main("1030875658")

#-End-------------------------------------------------------------------
