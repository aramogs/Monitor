"""
Semi Finished Functions

Functions for semi finished products, currently used for Vulcanized Hoses

"""
import re
import json
import requests

from functions import SAP_ErrorWindows
from functions import SAP_Alive
from functions import SAP_Login

from functions.DB.Functions import *


from functions.SA import SAP_MFP11
from functions.SA import SAP_MFHU
from functions.SA import SAP_LB12


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


def handling_sa(inbound):
    """
    Function takes Material Number, Quatity and creates a Handling unit
    Gets the serial number and returns it to the client
    If there are no errors the function prints a label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]

    subline = inbound["subline"]
    station = inbound["station"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]

    response = json.loads(SAP_MFP11.Main(con, storage_location, material[1:], cantidad))

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

        r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/SUB/Execute/', data=json.dumps(data))
        # print(r.text)

    if error == "":
        sap_error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)


def transfer_sa(inbound):
    """
    Function takes a Handling Unit number and creates a backflush
    If there are no errors the function returns a transfer order number
    """
    station = inbound["station"]
    serial_num = inbound["serial_num"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]

    product_version = DB.select_product_version(station)

    if product_version[0][0] is None:
        return json.dumps({"result": "N/A", "error": f'Product Version not configured for station: {station}'})

    response = json.loads(SAP_MFHU.Main(con, storage_location, product_version[0][0], serial_num))

    result = response["result"]
    error = response["error"]

    if error == "N/A":
        response2 = json.loads(SAP_LB12.Main(con, serial_num))
        result = response2["result"]

    response = {"serial": serial_num, "result": f'"{result}"', "error": error}
    return json.dumps(response)


def reprint_sa(inbound):
    """
    Function takes the necessary information to reprint a Handling Unit label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    subline = inbound["subline"]
    station = inbound["station"]
    serial_num = inbound["serial_num"]
    # con = inbound["con"]
    # storage_location = inbound["storage_location"]

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
        f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/SUB/Execute/', data=json.dumps(data))
    # print(r.text)

    response = {"serial": serial_num, "result": f'"Reprint OK"', "error": "N/A"}
    return json.dumps(response)

