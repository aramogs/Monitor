"""

Cycle Count Functions

Functions for Cycle count, currently used to count raw material and finish goods possibly vulcanized hoses as well


"""

import json
import re
from functions.DB.Functions import *

from functions.CC import SAP_LX03

from functions import SAP_Alive
from functions import SAP_Login
from functions import SAP_ErrorWindows
from functions.CC import SAP_LT09_Transfer
from functions import SAP_LS11


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


def cycle_count_status(inbound):
    """
        Functions takes a Finished Goods serial number and finds
        the corresponding material number
    """
    storage_type = inbound["storage_type"]
    storage_bin = inbound["storage_bin"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]

    bin_exist = SAP_LS11.Main(con, storage_type, storage_bin)
    if json.loads(bin_exist)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f"Storage Bin does not exist at Storage Type {storage_type}"})

    else:
        result_lx03 = json.loads(SAP_LX03.Main(con, storage_location, storage_type, storage_bin))

        if result_lx03["error"] != "N/A":
            response = json.dumps({"storage_units": "N/A", "error": f'{result_lx03["error"]}'})
            if result_lx03["error"] == "":
                sap_error_windows()
        else:
            response = json.dumps({"storage_units": result_lx03["result"], "error": "N/A"})
    return response


def cycle_count_transfer(inbound):
    storage_type = inbound["storage_type"]
    storage_bin = inbound["storage_bin"]
    station = re.sub(":", "-", inbound["station"])
    st = ""
    sb = ""
    emp_num = inbound["user_id"]
    not_found_response = ""
    unlisted_response = ""
    con = inbound["con"]
    storage_location = inbound["storage_location"]

    #############################################################################################################################################
    #############################################################################################################################################
    #############################################################################################################################################
    # TODO CHANGE ACCORDINGLY EVERY NEW STORAGE TYPE IS NEEDED
    # In case an storage unit was in the bin but not physically the storage unit will be transfer to storage bin CICLICOFG or CICLICOMP
    # For finished goods the storage type after the transfer will change to 901 this to not interrupt master label creation as FG does not allow it
    # In case an storage unit was physically but not in the bin the material will be transfer to the same bin

    if storage_type == "FG":
        st = "901"
        sb = "CICLICOFG"
    elif storage_type == "MP1":
        st = storage_type
        sb = "CICLICRAW1"
    elif storage_type == "MP":
        st = storage_type
        sb = "CICLICORAW"
    elif storage_type == "EXT":
        st = storage_type
        sb = "CICLICOEXT"
    elif storage_type == "VUL":
        st = storage_type
        sb = "CICLICOVUL"
    else:
        return json.dumps({"serial": "N/A", "error": f"Storage Type not configured for Cycle Control {storage_type}"})
    #############################################################################################################################################
    #############################################################################################################################################
    #############################################################################################################################################

    if len(inbound["not_found_storage_units"]) > 0:
        not_found_storage_units = inbound["not_found_storage_units"].split(",")
        response = SAP_LT09_Transfer.Main(con, not_found_storage_units, st, sb, station)
        not_found_response = json.loads(response)["result"].strip("][")

        for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
            if type(x['result']) == int:
                DB.insert_cycle_transfer(storage_type=storage_type, storage_bin=storage_bin, storage_unit=x["serial_num"], emp_num=emp_num, status="NOSCAN", sap_result=x["result"])
                pass
            else:
                DB.insert_cycle_transfer(storage_type=storage_type, storage_bin=storage_bin, storage_unit=x["serial_num"], emp_num=emp_num, status="NOSCAN-ERROR", sap_result=x["result"])
                pass

    if len(inbound["unlisted_storage_units"]) > 0:
        unlisted_storage_units = inbound["unlisted_storage_units"].split(",")
        response = SAP_LT09_Transfer.Main(con, unlisted_storage_units, storage_type, storage_bin, station)
        unlisted_response = json.loads(response)["result"].strip("][")

        for x in json.loads(re.sub(r"'", "\"", json.loads(response)["result"])):
            if type(x['result']) == int:
                DB.insert_cycle_transfer(storage_type=storage_type, storage_bin=storage_bin, storage_unit=x["serial_num"], emp_num=emp_num, status="WRONGBIN", sap_result=x["result"])
                pass
            else:
                DB.insert_cycle_transfer(storage_type=storage_type, storage_bin=storage_bin, storage_unit=x["serial_num"], emp_num=emp_num, status="WRONGBIN-ERROR", sap_result=x["result"])
                pass

    response = json.dumps({"result": f'{not_found_response + "," + unlisted_response}', "error": "N/A"})
    if json.loads(response)["error"] != "N/A":
        response = json.dumps({"serial": "N/A", "error": f'{response["error"]}'})
    return response
