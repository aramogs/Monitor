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
from functions.VU import SAP_LS11
from functions.VU import SAP_LT09_Transfer_Multiple
from functions.VU import SAP_LT09_Query
from functions.VU import SAP_LS24
from functions.VU import SAP_LT09_Audit

from functions.VU import SAP_MFP11
from functions.VU import SAP_MFHU
from functions.VU import SAP_LB12
from functions.VU import SAP_LT09
from functions.VU import SAP_LT01


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


def transfer_vul_serial(inbound):
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


def transfer_vul_material(inbound):
    """
        Functions takes a Finished Goods serial number and finds
        the corresponding material number
    """
    material = inbound["material"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    response = SAP_LS24.Main(con, storage_location, material)
    return response


def transfer_vul_mandrel(inbound):
    """
        Functions takes a Finished Goods serial number and finds
        the corresponding material number
    """
    material = inbound["material"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    response = SAP_LS24.Main(con, storage_location, material)
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
            DB.insert_complete_transfer(emp_num=emp_num, no_serie=x["serial_num"], result=x["result"], area="VUL", storage_bin=storage_bin)
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

        r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC/Execute/', data=json.dumps(data))
        # print(r.text)

    if error == "":
        sap_error_windows()

    response = {"serial": f'{serial_num}', "result": f'"{result}"', "error": error}
    return json.dumps(response)


def transfer_sf(inbound):
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


def transfer_sfr(inbound):
    """
    Function takes a serial number and performs a transfer of the material
    If everything goes right the function returns a transfer order
    """
    serial_num = inbound["serial_num"]
    con = inbound["con"]
    # storage_location = inbound["storage_location"]

    # TODO si no es storage type VUL no hacer transferencia
    if len(str(serial_num)) < 10:
        serial_num = "0"+str(serial_num)
    response = json.loads(SAP_LT09.Main(con, serial_num))

    result = response["result"]
    error = response["error"]

    if error == "":
        sap_error_windows()

    response = {"serial": serial_num, "result": f'"{result}"', "error": error}
    return json.dumps(response)


def transfer_sfr_return(inbound):
    """
    Function takes necessary information to perform a transfer order and print a corresponding label
    """
    material = inbound["material"]
    cantidad = inbound["cantidad"]
    subline = inbound["subline"]
    station = inbound["station"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]

    response = json.loads(SAP_LT01.Main(con, storage_location, material[1:], cantidad))

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

        r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC_RE/Execute/', data=json.dumps(data))
        # print(r.text)

    response = {"serial": serial_num, "result": f'"{transfer_order}"', "error": error}
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
        f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC/Execute/', data=json.dumps(data))
    # print(r.text)

    response = {"serial": serial_num, "result": f'"Reprint OK"', "error": "N/A"}
    return json.dumps(response)


def reprint_sfr(inbound):
    """
    Functions reprints a corresponding label
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
        f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/VULC_RE/Execute/',
        data=json.dumps(data))
    # print(r.text)

    response = {"serial": serial_num, "result": f'"Reprint OK"', "error": "N/A"}
    return json.dumps(response)
