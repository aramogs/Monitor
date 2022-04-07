import json

from functions import SAP_Alive
from functions import SAP_Login
from functions import SAP_ErrorWindows
from functions.RW import SAP_LS24
from functions.RW import SAP_LT01


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


def transfer_rework_in(inbound):
    # {"station":"700","material":"P5V0005305195","cantidad":"1","process":"transfer_rework_in","serial_num":"N/A"}
    sap_num = inbound["material"]
    quantity = inbound["cantidad"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    from_stype = "102"
    from_sbin = "103"
    to_stype = "102"
    to_sbin = "RETRABAJO"

    response = json.loads(SAP_LS24.Main(con, sap_num[1:], from_stype, from_sbin))
    if response["error"] != "N/A":
        return json.dumps({"serial": "N/A", "result": "N/A", "error": f'{response["error"]}'})
    else:
        if int(response["result"]) < int(quantity):
            err = round(((int(quantity) - int(response["result"])) / int(response["result"]))*100, 2)
            return json.dumps({"serial": "N/A", "result": "N/A", "error": f'Requested amount exceeded by {err}% of avaiable material'})
        else:
            response = json.loads(SAP_LT01.Main(con, sap_num[1:], quantity, from_stype, from_sbin, to_stype, to_sbin))

        return json.dumps(response)


def transfer_rework_out(inbound):
    # {"station":"700","material":"P5V0005305195","cantidad":"1","process":"transfer_rework_in","serial_num":"N/A"}
    sap_num = inbound["material"]
    quantity = inbound["cantidad"]
    con = inbound["con"]
    storage_location = inbound["storage_location"]
    from_Stype = "102"
    from_Sbin = "RETRABAJO"
    to_Stype = "102"
    to_Sbin = "103"

    response = json.loads(SAP_LS24.Main(con, sap_num[1:], from_Stype, from_Sbin))
    if response["error"] != "N/A":
        return json.dumps({"serial": "N/A", "result": "N/A", "error": f'{response["error"]}'})
    else:
        if int(response["result"]) < int(quantity):
            err = round(((int(quantity) - int(response["result"])) / int(response["result"])) * 100, 2)
            return json.dumps({"serial": "N/A", "result": "N/A",
                               "error": f'Requested amount exceeded by {err}% of avaiable material'})
        else:
            response = json.loads(SAP_LT01.Main(con, sap_num[1:], quantity, from_Stype, from_Sbin, to_Stype, to_Sbin))

        return json.dumps(response)
