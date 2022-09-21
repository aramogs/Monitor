"""
Raw Material Functions

Functions for Raw Materials at the warehouse

Created to transfer material between bins

"""

import json
import re

import requests

from functions.DB.Functions import *
from functions import SAP_Alive
from functions import SAP_Login
from functions import SAP_ErrorWindows
from functions.RM import SAP_LT01
from functions.RM import SAP_MM03
from functions.RM import SAP_LT09

current_directory = os.path.abspath(os.getcwd())


def partial_transfer(inbound):
    """
    Function takes a serial number and gets the material number, description and current quantity
    After that it returns the requested information
    """
    try:

        serial_num = inbound["serial_num"]
        con = inbound["con"]
        # storage_location = inbound["storage_location"]

        response = json.loads(SAP_LT09.Main(con, serial_num))
        storage_type = response["storage_type"]
        if storage_type != "MP":
            response = {"serial": "N/A", "material": "N/A", "material_description": "N/A", "material_w": "N/A", "cantidad": "N/A",
                        "error": "Partial Transfer only available for Storage Type MP", "certificate_number": "N/A"}
            return json.dumps(response)

        material_number = response["material_number"]
        material_description = response["material_description"]
        quant = response["quant"].replace(".000", "").replace(",", "")
        certificate_number = response["certificate_number"]

        error = response["error"]

        if material_number != "N/A":
            material_w = json.loads(SAP_MM03.Main(con, material_number))["net_weight"]

        else:
            material_w = "N/A"

        if error == "":
            sap_error_windows()

        response = {"serial": serial_num, "material": material_number, "material_description": material_description, "material_w": material_w, "cantidad": quant, "error": error,
                    "certificate_number": certificate_number}
        return json.dumps(response)
    except KeyError:
        response = {"serial": "N/A", "material": "N/A", "material_description": "N/A", "material_w": "N/A", "cantidad": "N/A", "error": "VERIFY JSON", "certificate_number": "N/A"}
        return json.dumps(response)


def partial_transfer_confirmed(inbound):
    """
    Function takes the necessary information to perform a transfer order
    Function gets the serial number of a Handling Unit and withdraws the requested material from it
    After that prints a label
    """
    station = inbound["station"]
    serial_num = inbound["serial_num"]
    material = inbound["material"]
    material_description = inbound["material_description"]
    cantidad = inbound["cantidad"]
    cantidad_restante = inbound["cantidad_restante"]
    user_id = inbound["user_id"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    certificate_number = inbound["certificate_number"]

    response = json.loads(SAP_LT01.Main(con, storage_location, material, cantidad, serial_num))
    result = response["result"]
    error = response["error"]

    if error == "":
        sap_error_windows()

    if re.sub(r"\D", "", result, 0) != "":
        result_insert = int(re.sub(r"\D", "", result, 0))
        if int(result_insert) != 0 or error != "N/A":
            if int(cantidad_restante) > 0:
                print_label(station, material, material_description, serial_num, certificate_number, cantidad_restante, "TRA")
            print_label(station, material, material_description, serial_num, certificate_number, cantidad, "TRAB")
            # if len(station) > 5:
            #     station = "web"
            DB.insert_partial_transfer(emp_num=user_id, part_num=material, no_serie=serial_num, linea=station,
                                       transfer_order=result_insert)
    else:
        error = result

    response = {"serial": serial_num, "material": material, "cantidad": cantidad, "result": f'"{result}"', "error": error}
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


def print_label(station, material, material_description, serial, lote, cantidad_restante, label):
    """
    Function prints the corresponding label
    """
    # if len(station) > 5:
    #     station = "web"

    printer = DB.get_printer(f'{station}')

    data = {"material": f'{material}', "descripcion": f'{material_description}', "serial": f'{serial}', "lote": f'{lote}', "cantidad": f'{cantidad_restante}',
            "printer": f'{printer}', "labels": "1"}

    r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/{label}/Execute/', data=json.dumps(data))
    print(r)
