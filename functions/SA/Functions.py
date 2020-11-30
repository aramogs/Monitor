import json
import os
import requests
from functions import SAP_ErrorWindows
from functions import SAP_Alive
from functions import SAP_Login
from functions.SA import SAP_LT09
from functions.SA import SAP_LT01
from db.Functions import *

current_directory = os.path.abspath(os.getcwd())


def transfer_sa(inbound):
    serial_num = inbound["serial_num"]
    response = json.loads(SAP_LT09.Main(serial_num))

    result = response["result"]
    error = response["error"]

    if error == "":
        sap_error_windows()

    response = {"serial": serial_num, "result": f'"{result}"', "error": error}
    return json.dumps(response)


def transfer_sa_return(inbound):
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    subline = inbound["subline"]
    station = inbound["station"]
    response = json.loads(SAP_LT01.Main(material[1:], cantidad))

    serial_num = response["serial"]
    transfer_order = response["result"]
    error = response["error"]

    if error != "N/A":
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
            f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC_RE_V2/Execute/',
            data=json.dumps(data))

    response = {"serial": serial_num, "result": f'"{transfer_order}"', "error": error}
    return json.dumps(response)


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
