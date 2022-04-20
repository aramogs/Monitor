"""
Semi Finished Functions

Functions for semi finished products, currently used for Vulcanized Hoses

"""
import re
import json

from functions import SAP_ErrorWindows
from functions import SAP_Alive
from functions import SAP_Login

from functions.DB.Functions import *
from functions.VU import SAP_LS11
from functions.VU import SAP_LT09_Transfer_Multiple
from functions.VU import SAP_LT09_Query
from functions.VU import SAP_LS24
from functions.VU import SAP_LT09_Audit


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


def transfer_vul(inbound):
    """
        Functions takes a Finished Goods serial number and finds
        the corresponding material number
    """
    serial_num = inbound["serial_num"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    result_lt09 = json.loads(SAP_LT09_Query.Main(con, serial_num))

    if result_lt09["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{result_lt09["error"]}'})
        if result_lt09["error"] == "":
            sap_error_windows()
    else:
        material_number = result_lt09["material_number"]
        response = SAP_LS24.Main(con, storage_location, material_number)
    return response


def transfer_vul_confirmed(inbound):
    """
        Function takes: Storage Type, Storage Bin, Serial number(s) and Employee Tag
        With this information the function Transfers the serial(s) to the corresponding Storage Bin
        And also saves this information to a database
    """
    storage_type = "VUL"
    storage_bin = inbound["storage_bin"]
    serials = (inbound["serial_num"]).split(",")
    emp_num = inbound["user_id"]
    station_hash = inbound["station"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]

    bin_exist = SAP_LS11.Main(con, storage_type, storage_bin)
    if json.loads(bin_exist)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f"Storage Bin does not exist at Storage Type {storage_type}"})
        # if json.loads(bin_exist)["error"] == "":
        #     response = json.dumps({f'"serial": "N/A", "error": "No Storage Bin like this in Storage Type {storage_type}"'})

    else:
        response = SAP_LT09_Transfer_Multiple.Main(con, serials, storage_type, storage_bin, station_hash)
        if json.loads(response)["error"] != "N/A":
            response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
            # re.sub("Busca comillas ' simples, se reemplazan con comillas dobles "
            # json.loads(response)["result"] carga la respuesta en formato json(Esta seccion convierte ' en "
            # json.loads(re.sub... Carga cada arreglo dentro de la respuesta a un json
            # for x in json.loads cada respuesta cargada del arreglo es iterada
        for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
            DB.insert_complete_transfer(emp_num=emp_num, no_serie=x["serial_num"], result=x["result"], area="VUL")
            pass

    return response


def audit_ext(inbound):
    """
        Function takes: Storage Type, Storage Bin, Serial number(s) and Employee Tag
        With this information the function Transfers the serial(s) to the corresponding Storage Bin
        And also saves this information to a database
    """
    serials = (inbound["serial_num"]).split(",")
    user_id = inbound["user_id"]
    station = inbound["station"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    storage_type = 102
    storage_bin = 103

    audit_response = json.loads(SAP_LT09_Audit.Main(con, serials, storage_type, storage_bin, station))

    for x in json.loads(re.sub(r"'", "\"", audit_response["result"])):
        DB.insert_audit_ext(x["serial"], user_id, x["sap_num"], x["sap_description"], x["error"])
    return json.dumps(audit_response)
