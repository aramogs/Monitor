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


from functions.SF import SAP_MFP11
from functions.SF import SAP_LT01
from functions.SF import SAP_LT09
from functions.SF import SAP_MFHU
from functions.SF import SAP_MFHU_Reverse
from functions.SF import SAP_LB12
from functions.SF import SAP_LB12_EXT
from functions.SF import SAP_LT09_EXT_RP
from functions.SF import SAP_LT01_EXT_PR
from functions.SF import SAP_LS24
from functions.DB.Functions import *

from functions import SAP_LS11
from functions import SAP_LT09_Transfer_Redis
from functions.SF import SAP_LT09_Query
from functions.SF import SAP_LS24_EXT

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
        print(r.text)

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

    response = {"serial": serial_num, "result": f'"{result}"', "error": error}
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
        user_id = inbound['user_id']

        response = json.loads(SAP_MFHU.Main(serial))

        error = response["error"]
        if error == 'N/A':
            transfer = json.loads(SAP_LB12_EXT.Main(serial))
            error = transfer["error"]
            if error == 'N/A':
                DB.acred_print_ext(serial, transfer['result'], user_id)
                response_list.append(response)
            else:
                DB.acred_print_error_ext(serial, transfer['error'], user_id)
                response_list.append(transfer)
                SAP_MFHU_Reverse.Main(serial)
                pass
        else:
            response_list.append(response)

    return json.dumps({"result": response_list, "error": error})


def transfer_ext_rp(inbound):
    """
    Function takes necessary information to perform a transfer order
    """
    material_list = inbound['data']
    emp_num = inbound['user_id']
    response_list = []
    for material in material_list:

        serial = material["serial"]
        plan_id = material["plan_id"]
        numero_parte = material["numero_parte"]
        cantidad = material["cantidad"]
        from_Sbin = "EXT"
        to_Sbin = "GREEN"

        if len(str(serial)) < 10:
            serial = "0" + str(serial)

        response = SAP_LT09_EXT_RP.Main(serial, to_Sbin)
        if json.loads(response)["error"] == "N/A":
            DB.trannsfer_print_ext(serial, json.loads(response)['result'], emp_num)
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
    cantidad = inbound["cantidad"]
    station = inbound["station"]
    operator_name = inbound["operator_name"]
    numero_etiquetas = inbound["numero_etiquetas"]
    operator_id = inbound["operator_id"]
    plan_id = inbound["plan_id"]
    impresoType = inbound["impresoType"]

    response_list = []
    for i in range(numero_etiquetas):
        response = json.loads(SAP_MFP11.Main(material, cantidad))

        serial_num = response["serial_num"]
        error = response["error"]
        result = response["result"]
        response_list.append({"serial_num": f'{serial_num}', "result": f'{result}', "error": error})

        if error == "N/A":
            printe = DB.select_printer_ext(station)
            printer = printe[0][0]

            result2 = DB.search_union_ext(material)
            columns = result2[0]
            values = result2[1]

            data = json.loads('{}')

            for column, value in zip(columns, values):
                data.update({column[0]: f'{value}'})

                data.update({"printer": f'{printer}'})
                data.update({"serial": f'{serial_num}'})
                data.update({"quant": f'{cantidad}'})
                data.update({"line": f'{station}'})
                data.update({"emp_num": f'{operator_name}'})

            r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/EXT/Execute/', data=json.dumps(data))
            print(r)
            if r.status_code == 200:
                DB.update_plan_ext(plan_id)
                DB.update_print_ext(serial_num, plan_id, material, operator_id, cantidad, impresoType)

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
    station = inbound["station"]
    operator_name = inbound["operator_name"]
    operator_id = inbound["operator_id"]
    impresoType = inbound["impresoType"]
    from_Sbin = "GREEN"
    to_Sbin = "TEMPR"
    # printer = f'\\\\tftdelsrv003\{inbound["impresora"]}'

    response = json.loads(SAP_LS24.Main(numero_parte, from_Sbin))
    if response["error"] != "N/A":
        return json.dumps({"serial": "N/A", "result": "N/A", "error": f'{response["error"]}'})
    else:
        if int(response["result"]) < int(cantidad):
            err = round(((int(cantidad) - int(response["result"])) / int(response["result"])) * 100, 2)
            return json.dumps({"serial": "N/A", "transfer_order": "N/A", "error": f'Requested amount exceeded by {err}% of available material'})
        else:
            response = json.loads(SAP_LT01_EXT_PR.Main(numero_parte, cantidad, from_Sbin, to_Sbin))
            serial_num = response["serial"]
            result_ext_pr = response["result"]
            error = response["error"]
            if error == "N/A":
                printe = DB.select_printer_ext(station)
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
                    data.update({"line": f'{station}'})
                    data.update({"emp_num": f'{operator_name}'})

                r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/EXT_RE/Execute/', data=json.dumps(data))
                if r.status_code == 200:
                    if serial_obsoleto != "undefined":
                        DB.update_plan_ext(plan_id)
                        DB.update_print_ext_return(serial_obsoleto,result_ext_pr)
                    DB.update_print_ext(serial_num, plan_id, numero_parte, operator_id, cantidad, impresoType)
            else:
                response = {"serial": "N/A", "result": "N/A", "error": error}

    transfer_order = response["result"]
    error = response["error"]
    response = {"serial": serial_num, "transfer_order": transfer_order, "error": error}
    print("RESPONSE", response)
    return json.dumps(response)


def transfer_ext(inbound):
    """
        Functions takes a Finished Goods serial number and finds
        the corresponding material number
    """
    serial_num = inbound["serial_num"]
    result_lt09 = json.loads(SAP_LT09_Query.Main(serial_num))

    if result_lt09["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{result_lt09["error"]}'})
        if result_lt09["error"] == "":
            sap_error_windows()
    else:
        material_number = result_lt09["material_number"]
        response = SAP_LS24_EXT.Main(material_number)
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

    bin_exist = SAP_LS11.Main(storage_type, storage_bin)
    if json.loads(bin_exist)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f"Storage Bin does not exist at Storage Type {storage_type}"})
        # if json.loads(bin_exist)["error"] == "":
        #     response = json.dumps({"serial": "N/A", "error": "No Storage Bin like this in Storage Type FG"})

    else:
        response = SAP_LT09_Transfer_Redis.Main(serials, storage_type, storage_bin, station_hash)
        if json.loads(response)["error"] != "N/A":
            response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
            # re.sub("Busca comillas ' simples, se reemplazan con comillas dobles "
            # json.loads(response)["result"] carga la respuesta en formato json(Esta seccion convierte ' en "
            # json.loads(re.sub... Carga cada arreglo dentro de la respuesta a un json
            # for x in json.loads cada respuesta cargada del arreglo es iterada
        for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
            DB.insert_complete_transfer(emp_num=emp_num, no_serie=x["serial_num"], result=x["result"], area="FG")
            pass

    return response
