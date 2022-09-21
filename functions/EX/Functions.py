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


from functions.EX import SAP_MFP11
from functions.EX import SAP_MFHU
from functions.EX import SAP_MFHU_Reverse
from functions.EX import SAP_LB12_EXT
from functions.EX import SAP_LT09_EXT_RP
from functions.EX import SAP_LT01_EXT_PR
from functions.EX import SAP_LS24
from functions.EX import SAP_LT09_EXT_RUBBER
from functions.DB.Functions import *

from functions.EX import SAP_LS11
from functions.EX import SAP_LT09_Transfer_Redis
from functions.EX import SAP_LT09_Query
from functions.EX import SAP_LS24_EXT


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


def confirm_ext_hu(inbound):

    material_list = inbound['data']
    station = inbound["station"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    response_list = []


    product_version = DB.select_product_version(station)

    if product_version[0][0] is None:
        return json.dumps({"result": "N/A", "error": f'Product Version cot configured for station: {station}'})

    for material in material_list:
        serial = material['serial']
        user_id = inbound['user_id']

        response = json.loads(SAP_MFHU.Main(con, storage_location, product_version[0][0], serial))
        error = response["error"]

        if error == 'N/A':
            transfer = json.loads(SAP_LB12_EXT.Main(con, serial))
            error = transfer["error"]
            if error == 'N/A':
                DB.acred_print_ext(serial, transfer['result'], user_id)
                response_list.append(response)
            else:
                DB.acred_print_error_ext(serial, transfer['error'], user_id)
                response_list.append(transfer)
                SAP_MFHU_Reverse.Main(con, product_version[0][0], serial)
                pass
        else:
            response_list.append(response)

    return json.dumps({"result": response_list, "error": error})


def transfer_ext_rp(inbound):
    """
    Function takes necessary information to perform a transfer order
    :param inbound: Json string containing all the information
    """
    material_list = inbound['data']
    emp_num = inbound['user_id']
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    response_list = []

    for material in material_list:

        serial = material["serial"]
        to_sbin = "GREEN"

        if len(str(serial)) < 10:
            serial = "0" + str(serial)

        response = SAP_LT09_EXT_RP.Main(con, serial, to_sbin)
        if json.loads(response)["error"] == "N/A":
            DB.transfer_print_ext(serial, json.loads(response)['result'], emp_num)
        response_list.append(json.loads(response))

    response = {"serial": "", "result": response_list, "error": "N/A"}
    return json.dumps(response)


def handling_ext(inbound):
    """
    Function takes Material Number, Quatity and creates a Handling unit
    Gets the serial number and returns it to the client
    If there are no errors the function prints a label
    """
    material = inbound["material"]
    quantity = inbound["cantidad"]
    line = inbound["line"]
    station = inbound["station"]
    operator_name = inbound["operator_name"]
    label_quantity = inbound["numero_etiquetas"]
    operator_id = inbound["operator_id"]
    plan_id = inbound["plan_id"]
    print_type = inbound["impresoType"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]

    response_list = []
    for i in range(label_quantity):
        response = json.loads(SAP_MFP11.Main(con, storage_location, material, quantity))

        serial_num = response["serial_num"]
        error = response["error"]
        result = response["result"]
        response_list.append({"serial_num": f'{serial_num}', "result": f'{result}', "error": error})

        if error == "N/A":
            printe = DB.select_printer(station)
            printer = printe[0][0]

            result2 = DB.search_union_ext(material)
            columns = result2[0]
            values = result2[1]

            data = json.loads('{}')

            for column, value in zip(columns, values):
                data.update({column[0]: f'{value}'})

                data.update({"printer": f'{printer}'})
                data.update({"serial": f'{serial_num}'})
                data.update({"quant": f'{quantity}'})
                data.update({"line": f'{line}'})
                data.update({"emp_num": f'{operator_name}'})

            r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/EXT/Execute/', data=json.dumps(data))
            if r.status_code == 200:
                DB.update_plan_ext(plan_id)
                DB.update_print_ext(serial_num, plan_id, material, operator_id, quantity, print_type)

            if error == "":
                sap_error_windows()

    response = {"result": f'"{response_list}"', "error": error}
    return json.dumps(response)


def storage_unit_ext_pr(inbound):
    """
       Function takes necessary information to perform a transfer order
    """
    serial_obsoleto = inbound["serial_num"]
    plan_id = inbound["plan_id"]
    numero_parte = inbound["material"]
    cantidad = inbound["cantidad"]
    line = inbound["line"]
    station = inbound["station"]
    operator_name = inbound["operator_name"]
    operator_id = inbound["operator_id"]
    printed_type = inbound["impresoType"]
    from_sbin = "GREEN"
    to_stype = "EXT"
    to_sbin = "TEMPR"
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    # printer = f'\\\\tftdelsrv003\{inbound["impresora"]}'

    response = json.loads(SAP_LS24.Main(con, storage_location, numero_parte, from_sbin))
    if response["error"] != "N/A":
        return json.dumps({"serial": "N/A", "result": "N/A", "error": f'{response["error"]}'})
    else:
        if int(response["result"]) < int(cantidad):
            err = round(((int(cantidad) - int(response["result"])) / int(response["result"])) * 100, 2)
            return json.dumps({"serial": "N/A", "transfer_order": "N/A", "error": f'Requested amount exceeded by {err}% of available material'})
        else:
            response = json.loads(SAP_LT01_EXT_PR.Main(con, storage_location, numero_parte, cantidad, from_sbin, to_stype, to_sbin))
            serial_num = response["serial"]
            result_ext_pr = response["result"]
            error = response["error"]
            if error == "N/A":
                printe = DB.select_printer(station)
                printer = printe[0][0]
                result2 = DB.search_union_ext(numero_parte)
                columns = result2[0]
                values = result2[1]

                data = json.loads('{}')

                for column, value in zip(columns, values):
                    data.update({column[0]: f'{value}'})

                    data.update({"printer": f'{printer}'})
                    data.update({"serial": f'{serial_num}'})
                    data.update({"quant": f'{cantidad}'})
                    data.update({"line": f'{line}'})
                    data.update({"emp_num": f'{operator_name}'})

                r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/EXT_RE/Execute/', data=json.dumps(data))
                if r.status_code == 200:
                    if serial_obsoleto != "undefined":
                        DB.update_plan_ext(plan_id)
                        DB.update_print_ext_return(serial_obsoleto, result_ext_pr)
                    DB.update_print_ext(serial_num, plan_id, numero_parte, operator_id, cantidad, printed_type)
            else:
                response = {"serial": "N/A", "result": "N/A", "error": error}

    transfer_order = response["result"]
    error = response["error"]
    response = {"serial": serial_num, "transfer_order": transfer_order, "error": error}
    return json.dumps(response)


def transfer_ext(inbound):
    """
        Functions takes a Finished Goods serial number and finds
        the corresponding material number
    """
    serial_num = inbound["serial_num"]
    con = inbound["con"]
    # storage_location = inbound["storage_location"]

    result_lt09 = json.loads(SAP_LT09_Query.Main(con, serial_num))

    if result_lt09["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{result_lt09["error"]}'})
        if result_lt09["error"] == "":
            sap_error_windows()
    else:
        material_number = result_lt09["material_number"]
        response = SAP_LS24_EXT.Main(con, material_number)
    return response


def transfer_ext_confirmed(inbound):
    """
        Function takes: Storage Type, Storage Bin, Serial number(s) and Employee Tag
        With this information the function Transfers the serial(s) to the corresponding Storage Bin
        And also saves this information to a database
    """
    storage_type = "EXT"
    storage_bin = inbound["storage_bin"]
    serials = (inbound["serial_num"]).split(",")
    emp_num = inbound["user_id"]
    station_hash = inbound["station"]
    con = inbound["con"]
    # storage_location = inbound["storage_location"]
    max_storage_unit_bin = 5

    bin_exist = SAP_LS11.Main(con, storage_type, storage_bin)
    serials_bin = len(serials) + int(json.loads(bin_exist)["quantity"])
    if json.loads(bin_exist)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f"Storage Bin does not exist at Storage Type {storage_type}"})
    # If storage bin begins with R then check if the amount of storage units exceeds 5 (Maximum amount of stare units per bin for Extrusion)
    elif storage_bin[0] == "r" or storage_bin[0] == "R" and serials_bin > max_storage_unit_bin:
        response = json.dumps({"serial": "N/A", "error": f"Exceeded amount of Storage Units per Bin: {serials_bin - max_storage_unit_bin}"})

    else:
        response = SAP_LT09_Transfer_Redis.Main(con, serials, storage_type, storage_bin, station_hash)
        if json.loads(response)["error"] != "N/A":
            response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
            # re.sub("Busca comillas ' simples, se reemplazan con comillas dobles "
            # json.loads(response)["result"] carga la respuesta en formato json(Esta seccion convierte ' en "
            # json.loads(re.sub... Carga cada arreglo dentro de la respuesta a un json
            # for x in json.loads cada respuesta cargada del arreglo es iterada
        for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
            DB.insert_complete_transfer(emp_num=emp_num, no_serie=x["serial_num"], result=x["result"], area="FG", storage_bin=storage_bin)
            pass

    return response


def verify_rubber(inbound):

    material = inbound["material"]
    storage_unit = inbound["serial_num"]
    operator_name = inbound["operator_name"]
    operator_id = inbound["operator_id"]
    con = inbound["con"]
    station = inbound["station"]
    extruder_line = inbound["line"]
    storage_location = inbound["storage_location"]
    to_sbin = "103"

    if len(str(storage_unit)) < 10:
        storage_unit = "0" + str(storage_unit)

    response_lt09_query = json.loads(SAP_LT09_Query.Main(con, storage_unit))

    if response_lt09_query["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{response_lt09_query["error"]}'})
    elif response_lt09_query["storage_location"] != storage_location:
        response = json.dumps({"serial": "N/A", "error": f'Verificar Storage Unit (SU),  '
                                                         f'Storage location del SU actual: {response_lt09_query["storage_location"]} '
                                                         f'Storage Location de {station}: {storage_location}'})
    else:
        if material != response_lt09_query["material_number"]:
            response = json.dumps({"serial": "N/A", "error": f'Verificar Storage Unit, numero de parte incorrecto'})
        else:
            response_lt09_rubber = json.loads(SAP_LT09_EXT_RUBBER.Main(con, storage_unit, to_sbin))
            if response_lt09_rubber["error"] != "N/A":
                response = json.dumps({"serial": "N/A", "error": f'{response_lt09_query["error"]}'})
            else:

                data = json.loads('{}')
                printe = DB.select_printer(station)
                printer = printe[0][0]

                data.update({"printer": f'{printer}'})
                data.update({"description": f'{response_lt09_query["material_description"]}'})
                data.update({"extruder": f'{extruder_line}'})
                data.update({"material": f'{material}'})
                data.update({"operator_id": f'{operator_id}'})
                data.update({"operator_name": f'{operator_name}'})
                data.update({"quantity": f'{response_lt09_query["quantity"]}'})
                data.update({"uom": f'{response_lt09_query["uom"]}'})
                data.update({"serial": f'{storage_unit}'})
                data.update({"transfer_order": f'{response_lt09_rubber["result"]}'})

                r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/EXT_RUB/Execute/', data=json.dumps(data))
                # print(r.text)

                response = json.dumps({"result": response_lt09_rubber["result"], "error": response_lt09_rubber["error"]})
            DB.update_ext_supply(material, f'{response_lt09_query["material_description"]}', extruder_line, f'{response_lt09_query["quantity"]}', operator_id, storage_unit, f'{response_lt09_rubber["result"]}')
    return response

