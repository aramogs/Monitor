"""
Semi Finished Functions

Functions for semi finished products, currently used for Vulcanized Hoses

"""
import json
import requests
from functions import SAP_ErrorWindows
from functions import SAP_Alive
from functions import SAP_Login


from functions.SF import SAP_MFP11
from functions.SF import SAP_LT01
from functions.SF import SAP_LT09
from functions.SF import SAP_MFHU
from functions.SF import SAP_LB12
from functions.SF import SAP_LB12_EXT
from functions.SF import SAP_LT01_EXT_RP
from functions.SF import SAP_LT01_EXT_PR
from functions.SF import SAP_LS24
from functions.SF import SAP_MFBF
from db.Functions import *


def sap_login():
    if json.loads(SAP_Alive.Main())["sap_status"] == "error":
        print("Error - SAP Connection Down")
        if json.loads(SAP_Login.Main())["sap_status"] != "ok":
            sap_login()
    else:
        # print("Success - SAP Connection Up")
        pass


def sap_error_windows():
    error = json.loads(SAP_ErrorWindows.error_windows())
    print(error)
    sap_login()

def handling_sf(inbound):
    """
    Function takes Material Number, Quatity and creates a Handling unit
    Gets the serial number and returns it to the client
    If there are no errors the function prints a label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]

    subline = inbound["subline"]
    station = inbound["station"]

    response = json.loads(SAP_MFP11.Main(material[1:], cantidad))

    serial_num = response["serial_num"]
    error = response["error"]
    result = response["result"]

    if error == "N/A":
        printe = DB.select_printer(station)
        printer = printe[0][0]

        result2 = DB.search_union(material)
        columns = result2[0]
        values = result2[1]

        data = json.loads('{}')

        for column, value in zip(columns, values):
            data.update({column[0]: f'{value}'})

        data.update({"printer": f'{printer}'})
        data.update({"serial_num": f'{serial_num}'})
        data.update({"real_quant": f'{cantidad}'})
        data.update({"line": f'{subline}'})

        r = requests.post(
            f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC/Execute/',
            data=json.dumps(data))
        # print(r.text)

    if error == "":
        sap_error_windows()


    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)


def transfer_sfr_return(inbound):
    """
    Function takes necessary information to perform a transfer order and print a corresponding label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    subline = inbound["subline"]
    station = inbound["station"]
    response = json.loads(SAP_LT01.Main(material[1:], cantidad))

    serial_num = response["serial"]
    transfer_order = response["result"]
    error = response["error"]

    if error == "N/A":
        printe = DB.select_printer(station)
        printer = printe[0][0]

        result = DB.search_union(material)
        columns = result[0]
        values = result[1]

        data = json.loads('{}')

        for column, value in zip(columns, values):
            data.update({column[0]: f'{value}'})

        data.update({"printer": f'{printer}'})
        data.update({"serial_num": f'{serial_num}'})
        data.update({"real_quant": f'{cantidad}'})
        data.update({"line": f'{subline}'})

        r = requests.post(
            f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC_RE/Execute/',
            data=json.dumps(data))
        # print(r.text)

    response = {"serial": serial_num, "result": f'"{transfer_order}"', "error": error}
    return json.dumps(response)


def transfer_sf(inbound):
    """
    Function takes a Handling Unit number and creates a backflush
    If there are no errors the function returns a transfer order number
    """
    serial_num = inbound["serial_num"]

    response = json.loads(SAP_MFHU.Main(serial_num))

    result = response["result"]
    error = response["error"]

    if error == "N/A":
        response2 = json.loads(SAP_LB12.Main(serial_num))
        result = response2["result"]

    response = {"serial": serial_num,"result": f'"{result}"', "error": error}
    return json.dumps(response)


def transfer_sfr(inbound):
    """
    Function takes a serial number and performs a transfer of the material
    If everything goes right the function returns a transfer order
    """
    serial_num = inbound["serial_num"]
    # TODO si no es storage type VUL no hacer transferencia
    if len(str(serial_num)) < 10:
        serial_num = "0"+str(serial_num)
    response = json.loads(SAP_LT09.Main(serial_num))

    result = response["result"]
    error = response["error"]

    if error == "":
        sap_error_windows()

    response = {"serial": serial_num, "result": f'"{result}"', "error": error}
    return json.dumps(response)


def reprint_sf(inbound):
    """
    Function takes the necessary information to reprint a Handling Unit label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    subline = inbound["subline"]
    station = inbound["station"]
    serial_num = inbound["serial_num"]

    # material = "P5000010050A0"
    # cantidad = "600"
    # subline = "2"
    # station = "700"
    # serial_num = "0123456789"

    printe = DB.select_printer(station)
    printer = printe[0][0]

    result = DB.search_union(material)
    columns = result[0]
    values = result[1]

    data = json.loads('{}')

    for column, value in zip(columns, values):
        data.update({column[0]: f'{value}'})

    data.update({"printer": f'{printer}'})
    data.update({"serial_num": f'{serial_num}'})
    data.update({"real_quant": f'{cantidad}'})
    data.update({"line": f'{subline}'})

    r = requests.post(
        f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC/Execute/',
        data=json.dumps(data))
    # print(r.text)

    response = {"serial": serial_num, "result": f'"Reprint OK"', "error": "N/A"}
    return json.dumps(response)


def confirm_ext_hu(inbound):
    material_list = inbound['data']
    response_list = []
    for material in material_list:

        numero_parte = material['numero_parte']
        cantidad = material['cantidad']
        serial = material['serial']
        plan_id = material['plan_id']

        response = json.loads(SAP_MFBF.Main(numero_parte, cantidad, serial, plan_id))
        response_list.append(response)
        if response['result'] != 'N/A':
            transfer = json.loads(SAP_LB12_EXT.Main())

    return json.dumps({"result": response_list, "error": "N/A"})


def transfer_ext_rp(inbound):
    """
    Function takes necessary information to perform a transfer order
    """
    material_list = inbound['data']
    response_list = []
    for material in material_list:

        serial = material["serial"]
        plan_id = material["plan_id"]
        numero_parte = material["numero_parte"]
        cantidad = material["cantidad"]
        from_Sbin = "103"
        to_Sbin = "GREEN"

        response = json.loads(SAP_LS24.Main(numero_parte, from_Sbin))
        if response["error"] != "N/A":
            response_list.append({"serial": serial, "transfer_order": "N/A", "error": f'{response["error"]}'})
        else:
            if int(response["result"]) < int(cantidad):
                err = round(((int(cantidad) - int(response["result"])) / int(response["result"])) * 100, 2)
                response_list.append({"serial": serial, "transfer_order": "N/A", "error": f'Requested amount exceeded by {err}% of available material'})
                # return json.dumps({"serial": "", "result": response_list, "error": "N/A"})
            else:
                response = json.loads(SAP_LT01_EXT_RP.Main(numero_parte, cantidad, from_Sbin, to_Sbin))

                transfer_order = response["result"]
                error = response["error"]
                response_list.append({"serial": serial, "transfer_order": transfer_order, "error": error})

    response = {"serial": "", "result": response_list, "error": "N/A"}
    return json.dumps(response)


def transfer_ext_pr(inbound):
    """
    Function takes necessary information to perform a transfer order
    """
    material_list = inbound['data']
    response_list = []
    for material in material_list:

        serial = material["serial"]
        plan_id = material["plan_id"]
        numero_parte = material["numero_parte"]
        cantidad = material["cantidad"]
        from_Sbin = "GREEN"
        to_Sbin = "103"

        response = json.loads(SAP_LS24.Main(numero_parte, from_Sbin))
        if response["error"] != "N/A":
            return json.dumps({"serial": "N/A", "result": "N/A", "error": f'{response["error"]}'})
        else:
            if int(response["result"]) < int(cantidad):
                err = round(((int(cantidad) - int(response["result"])) / int(response["result"])) * 100, 2)
                response_list.append({"serial": serial, "transfer_order": "N/A", "error": f'Requested amount exceeded by {err}% of available material'})
                return json.dumps({"serial": "", "result": response_list, "error": "N/A"})
            else:
                response = json.loads(SAP_LT01_EXT_PR.Main(numero_parte, cantidad, from_Sbin, to_Sbin))


        transfer_order = response["result"]
        error = response["error"]
        response_list.append({"serial": serial, "transfer_order": transfer_order, "error": error})

    response = {"serial": "", "result": response_list, "error": "N/A"}
    return json.dumps(response)

