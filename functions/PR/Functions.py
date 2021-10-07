import json
import requests


from functions.PR import SAP_MFP11
from functions.PR import SAP_Z_UC
from functions.PR import SAP_Z_UC_DEL
from functions.PR import SAP_Z_UC_WM
from functions.PR import SAP_MFP11_ALT
from functions.PR import SAP_MFHU
from functions.PR import SAP_LT09
from functions import SAP_ErrorWindows
from db.Functions import *


def create_pr_hu(inbound):
    """
      Function takes Material Number, Quantity and creates a Handling unit
      Gets the serial number and returns it to the client
      If there are no errors the function prints a label
      """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    employee = inbound["employee"]
    station = inbound["station"]

    response = json.loads(SAP_MFP11.Main(material[1:], cantidad))
    SAP_Z_UC.Main("dummy")
    serial_num = response["serial_num"]
    error = response["error"]
    result = response["result"]

    if error == "N/A":
        printe = DB.select_printer(station)
        printer = printe[0][0]

        result2 = DB.search_union(material)
        columns = result2[0]
        values = result2[1]
        table = result2[2]
        data = json.loads('{}')

        for column, value in zip(columns, values):
            data.update({column[0]: f'{value}'})

        data.update({"printer": f'{printer}'})
        data.update({"serial_num": f'{serial_num}'})
        data.update({"real_quant": f'{cantidad}'})
        data.update({"emp_num": f'{employee}'})
        data.update({"station": f'{station}'})
        data.update({"alternate_container": "NO"})

        r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/{table}/Execute/', data=json.dumps(data))
        # print(r.text)

    if error == "":
        SAP_ErrorWindows.error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)


def confirm_pr_hu(inbound):
    """
           Function takes a Handling Unit number and creates a back flush
    """
    serial_num = inbound["serial_num"]

    response = json.loads(SAP_MFHU.Main(serial_num))

    result = response["result"]
    error = response["error"]

    response = {"serial": serial_num, "result": f'"{result}"', "error": error}
    return json.dumps(response)


def confirm_pr_hu_transfer(inbound):
    """
        Function takes a Handling Unit number and creates a back flush
        If there are no errors the function returns a transfer order number
    """
    serial_num = inbound["serial_num"]

    response = json.loads(SAP_MFHU.Main(serial_num))

    result = response["result"]
    error = response["error"]
    if error[0] == "N/A":
        # response = {"serial": serial_num, "result": "OK", "error": "N/A"}
        # print("OK", response)
        # return json.dumps(response)
        response = json.loads(SAP_LT09.Main(serial_num))

        result = response["result"]
        error = response["error"]

        if error == "":
            SAP_ErrorWindows.error_windows()

        response = {"serial": serial_num, "result": f'"{result}"', "error": [error]}
        return json.dumps(response)
    else:
        response = {"serial": "N/A", "result": f'"{result}"', "error": error}
        # print("error", response)
        return json.dumps(response)


def no_confirm_pr_hu(inbound):
    """
            Function simulates to do a Back flush but does nothing
    """
    serial_num = inbound["serial_num"]

    response = {"serial": serial_num, "result": "OK", "error": ["N/A"]}
    return json.dumps(response)


def create_alternate_pr_hu(inbound):
    """
         Function takes Material Number, Quantity and creates a Handling unit
         Gets the serial number and returns it to the client
         If there are no errors the function prints a label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    employee = inbound["employee"]
    station = inbound["station"]

    response = json.loads(SAP_MFP11_ALT.Main(material[1:], cantidad))
    SAP_Z_UC.Main("dummy")
    serial_num = response["serial_num"]
    error = response["error"]
    result = response["result"]

    if error == "N/A":
        printe = DB.select_printer(station)
        printer = printe[0][0]

        result2 = DB.search_union(material)
        columns = result2[0]
        values = result2[1]
        table = result2[2]
        data = json.loads('{}')

        for column, value in zip(columns, values):
            data.update({column[0]: f'{value}'})

        data.update({"printer": f'{printer}'})
        data.update({"serial_num": f'{serial_num}'})
        data.update({"real_quant": f'{cantidad}'})
        data.update({"emp_num": f'{employee}'})
        data.update({"station": f'{station}'})
        data.update({"alternate_container": "YES"})

        r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/{table}/Execute/', data=json.dumps(data))
        # print(r.text)

    if error == "":
        SAP_ErrorWindows.error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)


def create_pr_hu_del(inbound):
    """
      Function takes Material Number, Quantity and creates a Handling unit
      Gets the serial number and returns it to the client
      If there are no errors the function prints a label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    station = inbound["station"]

    printe = DB.select_printer(station)
    printer = printe[0][0]

    response = json.loads(SAP_MFP11.Main(material[1:], cantidad))

    serial_num = response["serial_num"]
    error = response["error"]
    result = response["result"]

    result_z = json.loads(SAP_Z_UC_DEL.Main(printer))

    if result_z["error"] != "N/A":
        response = {"serial": "N/A", "result": "N/A", "error": result_z["error"]}
        return json.dumps(response)

    if error == "":
        SAP_ErrorWindows.error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)



def create_alt_pr_hu_del(inbound):
    """
      Function takes Material Number, Quantity and creates a Handling unit
      Gets the serial number and returns it to the client
      If there are no errors the function prints a label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    station = inbound["station"]

    printe = DB.select_printer(station)
    printer = printe[0][0]

    response = json.loads(SAP_MFP11_ALT.Main(material[1:], cantidad))

    serial_num = response["serial_num"]
    error = response["error"]
    result = response["result"]

    result_z = json.loads(SAP_Z_UC_DEL.Main(printer))

    if result_z["error"] != "N/A":
        response = {"serial": "N/A", "result": "N/A", "error": result_z["error"]}
        return json.dumps(response)

    if error == "":
        SAP_ErrorWindows.error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)


def create_pr_hu_wm(inbound):
    """
          Function takes Material Number, Quantity and creates a Handling unit
          Gets the serial number and returns it to the client
          If there are no errors the function prints a label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    station = inbound["station"]

    printe = DB.select_alt_printer(station)
    printer = printe[0][0]

    response = json.loads(SAP_MFP11.Main(material[1:], cantidad))

    serial_num = response["serial_num"]
    error = response["error"]
    result = response["result"]
    SAP_Z_UC.Main("dummy")
    result_z_wm = json.loads(SAP_Z_UC_WM.Main(printer, serial_num))

    if result_z_wm["error"] != "N/A":
        response = {"serial": "N/A", "result": "N/A", "error": result_z_wm["error"]}
        return json.dumps(response)

    if error == "":
        SAP_ErrorWindows.error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)



def create_alt_pr_hu_wm(inbound):
    """
          Function takes Material Number, Quantity and creates a Handling unit
          Gets the serial number and returns it to the client
          If there are no errors the function prints a label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    station = inbound["station"]

    printe = DB.select_alt_printer(station)
    printer = printe[0][0]

    response = json.loads(SAP_MFP11_ALT.Main(material[1:], cantidad))

    serial_num = response["serial_num"]
    error = response["error"]
    result = response["result"]
    SAP_Z_UC.Main("dummy")
    result_z_wm = json.loads(SAP_Z_UC_WM.Main(printer, serial_num))

    if result_z_wm["error"] != "N/A":
        response = {"serial": "N/A", "result": "N/A", "error": result_z_wm["error"]}
        return json.dumps(response)

    if error == "":
        SAP_ErrorWindows.error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)
