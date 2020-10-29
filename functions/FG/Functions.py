import json
import re
from db.Functions import *

from functions.FG import SAP_LS11
from functions.FG import SAP_LS24
from functions.FG import SAP_LT09_Query
from functions.FG import SAP_LT09_Transfer
from functions import SAP_Alive
from functions import SAP_Login
from functions import SAP_ErrorWindows


def transfer_fg(inbound):
    serial_num = inbound["serial_num"]
    result_lt09 = json.loads(SAP_LT09_Query.Main(serial_num))



    if result_lt09["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{result_lt09["error"]}'})
        if result_lt09["error"] == "":
            sap_error_windows()
    else:
        material_number = result_lt09["material_number"]
        response = SAP_LS24.Main(material_number)
    return response


def transfer_fg_confirmed(inbound):
    storage_bin = inbound["storage_bin"]
    serials = (inbound["serial_num"]).split(",")
    emp_num = inbound["user_id"]

    bin_exist = SAP_LS11.Main(storage_bin)
    if json.loads(bin_exist)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": "Storage Bin does not exist"})
        # if json.loads(bin_exist)["error"] == "":
        #     response = json.dumps({"serial": "N/A", "error": "No Storage Bin like this in Storage Type FG"})

    else:
        response = SAP_LT09_Transfer.Main(serials, storage_bin)
        if json.loads(response)["error"] != "N/A":
            response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
            # re.sub("Busca comillas ' simples, se reemplazan con comillas dobles "
            # json.loads(response)["result"] carga la respuesta en formato json(Esta seccion convierte ' en "
            # json.loads(re.sub... Carga cada arreglo dentro de la respuesta a un json
            # for x in json.loads cada respuesta cargada del arreglo es iterada
        for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
            DB.insert_complete_transfer(emp_num=emp_num, no_serie=x["serial_num"],result=x["result"])
            pass

    return response


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