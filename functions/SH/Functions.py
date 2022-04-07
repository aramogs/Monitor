"""

Shipments Functions

Functions for Shipment process, currently used to get Delivery information


"""

import json

from functions import SAP_Alive
from functions import SAP_ErrorWindows
from functions import SAP_Login
from functions.DB.Functions import *
from functions.SH import SAP_HU03V2
from functions.SH import SAP_HUMO
from functions.SH import SAP_LX03
from functions.SH import SAP_VL03N


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


def shipment_delivery_do_not_use(inbound):
    delivery = inbound["delivery"]
    stock = inbound["cantidad"]
    embarque = inbound["embarque"]
    list_of_lists = []

    result_search_delivery = DB.select_shipment_delivery(delivery)

    if len(result_search_delivery) != 0:
        response = json.dumps({"result": "N/A", "error": "Delivery already captured"})
        return response
    else:

        # start = time.time()
        response_sap_lx03 = json.loads(SAP_LX03.Main(delivery, stock))
        result_sap_lx03 = response_sap_lx03["result"]
        error_sap_lx03 = response_sap_lx03["error"]

        if error_sap_lx03 != "N/A":
            response = json.dumps({"result": "N/A", "error": f'{error_sap_lx03}'})
            return response
        else:

            response_sap_humo = SAP_HUMO.Main(result_sap_lx03)
            response_sap_hu03 = json.loads(SAP_HU03V2.Main())
            result_sap_hu03 = response_sap_hu03["result"]
            error_sap_hu03 = response_sap_hu03["error"]

            if error_sap_hu03 != "N/A":
                response = json.dumps({"result": "N/A", "error": f'{error_sap_hu03}'})
                return response
            else:
                for master_serials in json.loads(result_sap_hu03.replace("\'", "\"")):
                    if len(master_serials["serials"]) == 0:
                        _list = []
                        _list = [embarque, delivery, master_serials["master"], master_serials["master"]]
                        list_of_lists.append(tuple(_list))

                    for serial in master_serials["serials"]:
                        _list = []
                        _list = [embarque, delivery, master_serials["master"], serial]
                        list_of_lists.append(tuple(_list))

        insert_result = DB.insert_shipment_delivery(values_list=list_of_lists)
        response = json.dumps({"result": insert_result, "error": "N/A"})
        # print("\nTime", time.time() - start, "\n")
        return response


def shipment_delivery(inbound):
    delivery = inbound["delivery"]
    stock = inbound["cantidad"]
    embarque = inbound["embarque"]
    con = inbound["con"]
    # storage_location = inbound["storage_location"]
    list_of_lists = []

    result_search_delivery = DB.select_shipment_delivery(delivery)

    if len(result_search_delivery) != 0:
        response = json.dumps({"result": "N/A", "error": "Delivery already captured"})
        return response
    else:
        response_sap_vl03n = json.loads(SAP_VL03N.Main(con, delivery))
        result_sap_vl03n = response_sap_vl03n["result"]
        error_sap_vl03n = response_sap_vl03n["error"]
        if error_sap_vl03n != "N/A":
            response = json.dumps({"result": "N/A", "error": f'{error_sap_vl03n}'})
            return response
        else:
            response_sap_hu03 = json.loads(SAP_HU03V2.Main(con,))
            result_sap_hu03 = response_sap_hu03["result"]
            error_sap_hu03 = response_sap_hu03["error"]
            quantity_sap_hu03 = response_sap_hu03["real_quantity"]
            if error_sap_hu03 != "N/A":
                response = json.dumps({"result": "N/A", "error": f'{error_sap_hu03}'})
                return response
            else:
                if int(stock) != int(quantity_sap_hu03):
                    response = {"result": "N/A", "error": f'Shipment Quantity: {stock}, Delivery Quantity: {quantity_sap_hu03}'}
                    return json.dumps(response)
                else:
                    for master_serials in json.loads(result_sap_hu03.replace("\'", "\"")):
                        if len(master_serials["serials"]) == 0:
                            _list = []
                            _list = [embarque, delivery, master_serials["master"], master_serials["master"]]
                            list_of_lists.append(tuple(_list))

                        for serial in master_serials["serials"]:
                            _list = []
                            _list = [embarque, delivery, master_serials["master"], serial]
                            list_of_lists.append(tuple(_list))

                    insert_result = DB.insert_shipment_delivery(values_list=list_of_lists)
                    response = json.dumps({"result": insert_result, "error": "N/A"})
        # print("\nTime", time.time() - start, "\n")
        return response

#print(shipment_delivery({'station': 'a37ef516-e44f-423a-9ea1-7b58936cc6ee', 'serial_num': '', 'delivery': '80692028', 'cantidad': '1800', 'process': 'shipment_delivery', 'material': '', 'embarque': 'BMW2023'}))
