"""

Finished Goods Functions

Functions for finished goods products, currently used to transfer material between bins, and creation of GM master label


"""

import json
import re
# import datetime
import requests
from functions.DB.Functions import *

from functions.FG import SAP_LS24
from functions.FG import SAP_LT09_Query
from functions import SAP_LS11
from functions import SAP_LT09_Transfer
from functions import SAP_LT09_Transfer_Redis
from functions import SAP_LT09_Single_Transfer
from functions import SAP_Alive
from functions import SAP_Login
from functions import SAP_ErrorWindows
from functions.FG import SAP_LT09_Pack
from functions.FG import SAP_POP3
from functions.FG import SAP_HU02
from functions.FG import SAP_MM03
from functions.FG import SAP_HUMO


def sap_login():
    """
        Function checks if SAP is on or not
    """
    if json.loads(SAP_Alive.Main())["sap_status"] == "error":
        print("Error - SAP Connection Down")
        if json.loads(SAP_Login.Main())["sap_status"] != "ok":
            sap_login()
    else:
        # print("Success - SAP Connection Up")
        pass


def sap_error_windows():
    """
        Function to check if there are any error windows in the current computer regarding SAP
    """
    error = json.loads(SAP_ErrorWindows.error_windows())
    print(error)
    sap_login()


def transfer_fg(inbound):
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
        response = SAP_LS24.Main(con, material_number)
    return response


def transfer_fg_confirmed(inbound):
    """
        Function takes: Storage Type, Storage Bin, Serial number(s) and Employee Tag
        With this information the function Transfers the serial(s) to the corresponding Storage Bin
        And also saves this information to a database
    """
    storage_type = "FG"
    storage_bin = inbound["storage_bin"]
    serials = (inbound["serial_num"]).split(",")
    emp_num = inbound["user_id"]
    station_hash = inbound["station"]
    con = inbound["con"]
    # storage_location = inbound["storage_location"]

    bin_exist = SAP_LS11.Main(con, storage_type, storage_bin)
    if json.loads(bin_exist)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f"Storage Bin does not exist at Storage Type {storage_type}"})
        # if json.loads(bin_exist)["error"] == "":
        #     response = json.dumps({"serial": "N/A", "error": "No Storage Bin like this in Storage Type FG"})

    else:
        response = SAP_LT09_Transfer_Redis.Main(con, serials, storage_type, storage_bin, station_hash)
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


def master_fg_gm_verify(inbound):
    """
        Function takes: Serial number(s)
        With this information the function verify every serial number to see if it is created and available
    """
    serials = (inbound["serial_num"]).split(",")
    con = inbound["con"]
    # storage_location = inbound["storage_location"]

    response = SAP_HUMO.Main(con, serials)
    try:
        part_number = json.loads((re.sub(r"'", "\"", json.loads(response)["result"])))
        for x in part_number:
            if DB.search_union(f'P{x["part_number"]}') is None:
                return json.dumps({"serial": "N/A", "error": "Material information not available, contact customer service"})
    except:
        pass

    if json.loads(response)["error"] != "N/A":
        error = re.sub(r"'", "\"", json.loads(response)["error"])
        return json.dumps({"serial": "N/A", "error": f'{error}'})

    else:
        return response


def master_fg_gm_create(inbound):
    """
        Function takes: Serial number(s)
        With this information the function creates a Master Handling Unit and prints the corresponding GM label
        Also saves the information related to the label in a database
    """
    # As a requirement GM asks for the lower date of the handling units to be in the master label
    # This process takes the lower date from the inbound
    lower_date = datetime.datetime.strptime(f'{inbound["lower_gr_date"]}', "%Y-%m-%d").strftime("%Y%m%d")
    # Splitting the serial numbers from inbound
    serials = (inbound["serial_num"]).split(",")
    # Transferring every handling unit to Storage type: 923 and Storage bin: pack.bin
    # This transfer is in order to make them eligible for packing
    con = inbound["con"]
    # storage_location = inbound["storage_location"]
    response = json.loads(SAP_LT09_Pack.Main(con, serials))
    # Getting the source storage type and source storage bin for every serial number
    bin_list = response["bin_list"]
    # If there were errors doing the transfer return the error
    if response["error"] != "N/A":
        if len(bin_list) != 0:
            return_origen(con, bin_list)
        error = re.sub(r"'", "\"", response["error"])
        return json.dumps({"serial": "N/A", "error": f'{error}'})

    # If there were no errors take the part number from the response
    part_number = response["part_number"]
    client_part_number = DB.client_part_number(f'P{part_number}')
    # print(client_part_number[0])
    # Using the part number to get the container of the master label
    pop3_result = json.loads(SAP_POP3.Main(con, response["part_number"]))
    if pop3_result["error"] != "N/A":
        return_origen(con, bin_list)
        return json.dumps({"serial": "N/A", "error": f'{response}'})
    else:
        # Using the container number and the serial numbers HU02 creates the master handling unit
        # After creating the master handling unit it packs the serial numbers into itself
        # The response should be the master serial number
        packing_result = json.loads(SAP_HU02.Main(con, pop3_result["result"], part_number, client_part_number[0], serials))
        # If error is different than "N/A" return the error
        # Check SAP_HU02 for more information about errors
        if packing_result["error"] != "N/A":
            return_origen(con, bin_list)
            return json.dumps({"serial": "N/A", "error": f'{packing_result["error"]}'})
        else:
            # From the response and inbound take the following information

            single_container = packing_result["single_container"]
            mmo3_result = json.loads(SAP_MM03.Main(con, single_container))
            container_type = mmo3_result["container_type"]

            emp_num = inbound["user_id"]
            master_serial = packing_result["result"]
            total_weight = int(float(packing_result["gross_weigth"]))
            total_quant = int(round(float(re.sub(r",", "", packing_result["total_quantity"]))))
            # After the master HU is created the material remains in the same storage_type 923, storage_bin pack.bin
            # This process moves the material to a new location assigned by Logistics
            # Taking the master handling unit, storage type and storage bin
            response = json.loads(SAP_LT09_Transfer.Main(con, [packing_result["result"]], os.getenv("SAP_DEST_STYPE"), os.getenv("SAP_DEST_SBIN")))
            # Getting the result from the transfer order
            lt09_result = json.loads((re.sub(r"'", "\"", response["result"])))
            # Iterating the number of handling units to save the corresponding information in the data base
            # Saving Employee number, Handling Unit(UC), Master Handling Unit (UM) and Transfer Order
            for x in serials:
                DB.insert_master_transfer(emp_num, part_number, x, lt09_result[0]["serial_num"], lt09_result[0]["result"])
            # With this the station is forced into the code
            station = "402"
            # Used to get the printer judged by the station
            printe = DB.select_printer(station)
            printer = printe[0][0]
            # Getting all the information of the part number for the label
            result = DB.search_union(f'P{part_number}')
            columns = result[0]
            values = result[1]
            # Adding the remaining information for the label
            data = json.loads('{}')
            data.update({"printer": f'{printer}'})
            data.update({"serial_num": f'{master_serial[1:]}'})
            data.update({"fifo_date": f'{lower_date}'})
            data.update({"total_packs": f'{len(serials)}'})
            data.update({"total_quant": f'{total_quant}'})
            data.update({"qty_per_pack": f'{int(float(total_quant) / len(serials))}'})
            data.update({"total_weight": f'{total_weight}'})
            data.update({"container_type": f'{container_type}'})

            # Sending the post to the bartender integration service
            for column, value in zip(columns, values):
                data.update({column[0]: f'{value}'})
            r = requests.post(f'http://{os.getenv("BARTENDER_SERVER")}:{os.getenv("BARTENDER_PORT")}/Integration/GMMaster/Execute/', data=json.dumps(data))
            # print(r.status_code)
            # print(r.text)
        # Returning the information to the client
    return json.dumps(response)


def return_origen(con, bin_list):
    """
         Function takes: List of serial numbers with storage type and storage bin
         With this information the function transfers the material to the corresponding storage type and bin
    """
    # print(type(bin_list))
    for x in json.loads(re.sub(r"'", "\"", bin_list)):
        origen = json.loads(re.sub(r"'", "\"", json.dumps(x)))
        serial_num = origen["serial_num"]
        storage_type = origen["storage_type"]
        storage_bin = origen["storage_bin"]
        response = SAP_LT09_Single_Transfer.Main(con, serial_num, storage_type, storage_bin)
