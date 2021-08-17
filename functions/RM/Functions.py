"""
Raw Material Functions

Functions for Raw Materials at the warehouse

Created to transfer material between bins

"""

import json
import re

import requests

from db.Functions import *
from functions import SAP_Alive
from functions import SAP_Login
from functions import SAP_ErrorWindows
from functions import SAP_LS11
from functions import SAP_LT09_Transfer
from functions.RM import SAP_LT01
from functions.RM import SAP_MM03
from functions.RM import SAP_LT09
from functions.RM import SAP_SE16_MAKT
from functions.RM import SAP_LS24

current_directory = os.path.abspath(os.getcwd())


def partial_transfer(inbound):
    """
    Function takes a serial number and gets the material number, description and current quantity
    After that it returns the requested information
    """
    try:
        serial_num = inbound["serial_num"]

        response = json.loads(SAP_LT09.Main(serial_num))

        material_number = response["material_number"]
        material_description = response["material_description"]
        quant = response["quant"].replace(".000", "").replace(",", "")

        error = response["error"]

        if material_number != "N/A":
            material_w = material_weigth(material_number)
        else:
            material_w = "N/A"

        if error == "":
            sap_error_windows()

        response = {"serial": serial_num, "material": material_number, "material_description": material_description,
                    "material_w": material_w, "cantidad": quant, "error": error}
        return json.dumps(response)
    except KeyError:
        response = {"serial": "N/A", "material": "N/A", "material_description": "N/A",
                    "material_w": "N/A", "cantidad": "N/A", "error": "VERIFY JSON"}
        return json.dumps(response)


def material_weigth(_material):
    """
    Function takes material number, checks material weight and returns it
    """
    response = json.loads(SAP_MM03.Main(_material))
    return response["net_weight"]


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

    response = json.loads(SAP_LT01.Main(material, cantidad, serial_num))
    result = response["result"]
    error = response["error"]

    if error == "":
        sap_error_windows()

    if re.sub(r"\D", "", result, 0) != "":
        result_insert = int(re.sub(r"\D", "", result, 0))
        if int(result_insert) != 0 or error != "N/A":
            print_label(station, material, material_description, serial_num, cantidad_restante)
            if len(station) > 5:
                station = "web"
            DB.insert_partial_transfer(emp_num=user_id, part_num=material, no_serie=serial_num, linea=station,
                                       transfer_order=result_insert)
    else:
        error = result

    response = {"serial": serial_num, "material": material, "cantidad": cantidad, "result": f'"{result}"', "error": error}
    return json.dumps(response)


def transfer_mp_confirmed(inbound):
    """
    Function takes one or several serial numbers and performs the corresponding transfer orders to the corresponding bin
    After everything is done it sends a list of errors if there are any
    """
    storage_bin = inbound["storage_bin"]
    serials = (inbound["serial_num"]).split(",")
    emp_num = inbound["user_id"]
    storage_type = "MP1"

    bin_exist = SAP_LS11.Main(storage_type, storage_bin)
    if json.loads(bin_exist)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f"Storage Bin does not exist at Storage Type {storage_type}"})
    else:
        response = SAP_LT09_Transfer.Main(serials, storage_type, storage_bin)
        if json.loads(response)["error"] != "N/A":
            response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
            # re.sub("Busca comillas ' simples, se reemplazan con comillas dobles "
            # json.loads(response)["result"] carga la respuesta en formato json(Esta seccion convierte ' en "
            # json.loads(re.sub... Carga cada arreglo dentro de la respuesta a un json
            # for x in json.loads cada respuesta cargada del arreglo es iterada
        for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
            DB.insert_complete_transfer(emp_num=emp_num, no_serie=x["serial_num"], result=x["result"], area="RM")
            pass

    return response


def raw_delivery_verify(inbound):
    date = inbound["fecha"]
    user_id = inbound["user_id"]
    shift = inbound["turno"]
    sap_numbers = inbound["numeros_sap"]
    array_of_arrays = []
    sap_nums = []

    for sap_num in sap_numbers:
        sap_nums.append(str(sap_num[0]))

    se16_response = json.loads(SAP_SE16_MAKT.Main(sap_nums))
    if se16_response["error"] != "N/A":
        response = {"serial": "N/A", "error": se16_response["error"]}
    else:
        for material, containers in sap_numbers:
            array = []
            for x in se16_response["result"]:
                if x["material"] == material:
                    array.append(x["material"])
                    array.append(x["material_description"])
                    array.append(f'{containers}')
                    array.append(user_id)
                    array.append(shift)
                    array.append("Pendiente")
            array_of_arrays.append(tuple(array))

        insert_result = DB.insert_raw_delivery(values=array_of_arrays)
        response = {"result": f"{se16_response['result']}", "error": "N/A"}
    print(response)
    # response = json.dumps({"serial": "N/A", "error": f"N/A"})
    return json.dumps(response)


def raw_fifo_verify(inbound):
    print(inbound)

    material = inbound["material"]
    storage_type = inbound["storage_type"]
    response = json.loads(SAP_LS24.Main(material, storage_type))
    return json.dumps(response)


def raw_mp_confirmed(inbound):
    """
    Function takes one or several serial numbers and performs the corresponding transfer orders to the corresponding bin
    After everything is done it sends a list of errors if there are any
    """
    serials = (inbound["serial_num"]).split(",")
    emp_num = inbound["user_id"]
    raw_id = inbound["raw_id"]
    storage_type_db = inbound["storage_type"]
    storage_type = "102"
    storage_bin = "104"

    response = SAP_LT09_Transfer.Main(serials, storage_type, storage_bin)
    if json.loads(response)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
        # re.sub("Busca comillas ' simples, se reemplazan con comillas dobles "
        # json.loads(response)["result"] carga la respuesta en formato json(Esta seccion convierte ' en "
        # json.loads(re.sub... Carga cada arreglo dentro de la respuesta a un json
        # for x in json.loads cada respuesta cargada del arreglo es iterada
    for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
        DB.insert_raw_movement(raw_id=raw_id, storage_type=storage_type_db, emp_num=emp_num, no_serie=x["serial_num"], result=x["result"])
        pass
    return response


def raw_mp_confirmed_v(inbound):
    """
    Function takes one or several serial numbers and performs the corresponding transfer orders to the corresponding bin
    After everything is done it sends a list of errors if there are any
    """

    serials = (inbound["serial_num"]).split(",")
    emp_num = inbound["user_id"]
    raw_id = inbound["raw_id"]
    shift = inbound["shift"]
    storage_type = "MP"

    if shift == "T1":
        storage_bin = "H0110"
    elif shift == "T2":
        storage_bin = "H0111"
    elif shift == "T3":
        storage_bin = "H0112"

    response = SAP_LT09_Transfer.Main(serials, storage_type, storage_bin)
    if json.loads(response)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
        # re.sub("Busca comillas ' simples, se reemplazan con comillas dobles "
        # json.loads(response)["result"] carga la respuesta en formato json(Esta seccion convierte ' en "
        # json.loads(re.sub... Carga cada arreglo dentro de la respuesta a un json
        # for x in json.loads cada respuesta cargada del arreglo es iterada
    for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
        DB.insert_raw_movement(raw_id=raw_id, storage_type=storage_type, emp_num=emp_num, no_serie=x["serial_num"], result=x["result"])
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


def print_label(station, material, material_description, serial, cantidad_restante):
    """
    Function prints the corresponding label
    """
    if len(station) > 5:
        station = "web"

    printer = DB.get_printer(f'{station}')

    data = {"material": f'{material}', "descripcion": f'{material_description}', "serial": f'{serial}', "cantidad": f'{cantidad_restante}', "printer": f'{printer}'}

    r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/TRA/Execute/',
                      data=json.dumps(data))
    # print(r.text)
