import inspect
import queue
import signal
import time
import pika
import window
from threading import Thread
from tkinter import *


from functions.CC.Functions import *  # Control Cycle
from functions.FG.Functions import *  # Finished Goods
from functions.PR.Functions import *  # Production
from functions.RM.Functions import *  # Raw Material
from functions.RW.Functions import *  # Re Work
from functions.SA.Functions import *  # Sub Assembly
from functions.SF.Functions import *  # Semi Finished
from functions.SH.Functions import *  # Shipments
from functions.VU.Functions import *  # Vulcanized


#####################
# Window Functions
#####################
def quit_window():
    os.kill(os.getpid(), signal.SIGTERM)


def show_master_top(e):
    master_top.deiconify()
    master.withdraw()


def close_secondary():
    master.deiconify()
    master_top.withdraw()


def insert_text(request):
    inbound = json.loads(request)
    try:
        # station = inbound["station"]
        process = inbound["process"]
        global label_text
        # if len(station) > 5:
        #     station = "WEB"

        mainWindow.list.insert(END, f' Req    [{process.capitalize()}]    JSON:  {request}')
        mainWindow.list.see(END)
        label_text["text"] = f' Req    [{process.capitalize()}]    JSON:  {request}'
        master_top.lift()
    except KeyError:
        mainWindow.list.insert(END, f' Req    [Err] VERIFY JSON')
        mainWindow.list.see(END)
        label_text["text"] = f' Req    [Err] VERIFY JSON'


def insert_response_(response):
    inbound = json.loads(response)
    global label_text

    if inbound["error"] == "N/A":
        mainWindow.list.insert(END, f' Res     [Success]       JSON:   {inbound}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [Success]      JSON:   {inbound}'
        master_top.lift()
    else:
        mainWindow.list.insert(END, f' Res     [Error]:  {inbound["error"]}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [Success]:   {inbound["error"]}'
        master_top.lift()
#####################
# Window Functions
#####################


def sap_login():
    return SAP_Login.Main()


def error_logger(err):
    global pika_body
    now_ = datetime.datetime.now()
    error_t = now_.strftime("%Y-%m-%d_%H-%M")
    logging.basicConfig(filename='.\\logs\\error_{}.log'.format(error_t), filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.error(
        f'START - ########################################################################################\nJSON:     {pika_body}\nERROR: {err}',
        exc_info=True)  # Con esto se logea
    logging.error(f'END - ########################################################################################')
    # os.system(f'taskkill /im "Monitor.exe"')


def sap_connections(current_queue):
    qsize = sap_login_queue.qsize()
    sap_login_queue.get()
    result_sap_alive = json.loads(SAP_Alive.Main())
    if result_sap_alive["sap_status"] == "error" or result_sap_alive["connections"] < sap_login_queue.unfinished_tasks:
        print(f"[{current_queue}] Error SAP Connection Down")
        sap_login()
        if json.loads(SAP_Alive.Main())["connections"] < qsize:
            sap_connections(current_queue)


#####################
# Inbound Functions
#####################
def process_inbound_queue(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        # return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    ##############Raw Material##################
    if process == "partial_transfer":
        response = partial_transfer(inbound)
    elif process == "partial_transfer_confirmed":
        response = partial_transfer_confirmed(inbound)
    elif process == "transfer_mp_confirmed":
        response = transfer_mp_confirmed(inbound)
    elif process == "raw_delivery_verify":
        response = raw_delivery_verify(inbound)
    elif process == "raw_fifo_verify":
        response = raw_fifo_verify(inbound)
    elif process == "raw_mp_confirmed":
        response = raw_mp_confirmed(inbound)
    elif process == "raw_mp_confirmed_v":
        response = raw_mp_confirmed_v(inbound)
    elif process == "location_mp_material":
        response = location_mp_material(inbound)
    elif process == "location_mp_serial":
        response = location_mp_serial(inbound)
    ##############Finished Goods##################
    elif process == "transfer_fg":
        response = transfer_fg(inbound)
    elif process == "transfer_fg_confirmed":
        response = transfer_fg_confirmed(inbound)
    elif process == "master_fg_gm_verify":
        response = master_fg_gm_verify(inbound)
    elif process == "master_fg_gm_create":
        response = master_fg_gm_create(inbound)
    ##############Sub Assembly##################
    elif process == "transfer_sa":
        response = transfer_sa(inbound)
    elif process == "transfer_sa_return":
        response = transfer_sa_return(inbound)
    elif process == "reprint_sa":
        response = reprint_sa(inbound)
    ##############Semi Finished##################
    elif process == "handling_sf":
        response = handling_sf(inbound)
    elif process == "transfer_sf":
        response = transfer_sf(inbound)
    elif process == "transfer_sfr":
        response = transfer_sfr(inbound)
    elif process == "transfer_sfr_return":
        response = transfer_sfr_return(inbound)
    elif process == "reprint_sf":
        response = reprint_sf(inbound)
    ##############Re Work##################
    elif process == "transfer_rework_in":
        response = transfer_rework_in(inbound)
    elif process == "transfer_rework_out":
        response = transfer_rework_out(inbound)
    ##############Production##################
    elif process == "create_pr_hu":
        response = create_pr_hu(inbound)
    elif process == "confirm_pr_hu":
        response = confirm_pr_hu(inbound)
    elif process == "confirm_pr_hu_transfer":
        response = confirm_pr_hu_transfer(inbound)
    elif process == "no_confirm_pr_hu":
        response = no_confirm_pr_hu(inbound)
    elif process == "create_alternate_pr_hu":
        response = create_alternate_pr_hu(inbound)
    elif process == "create_pr_hu_del":
        response = create_pr_hu_del(inbound)
    elif process == "create_pr_hu_wm":
        response = create_pr_hu_wm(inbound)
    elif process == "create_alt_pr_hu_del":
        response = create_alt_pr_hu_del(inbound)
    elif process == "create_alt_pr_hu_wm":
        response = create_alt_pr_hu_wm(inbound)
    ##############Control Cycle##################
    # elif process == "cycle_count_status":
    #     response = cycle_count_status(inbound)
    # elif process == "cycle_count_transfer":
    #     response = cycle_count_transfer(inbound)
    ##############Extrusion##################
    # elif process == "handling_ext":
    #     response = handling_ext(inbound)
    # elif process == "confirm_ext_hu":
    #     response = confirm_ext_hu(inbound)
    # elif process == "transfer_ext_rp":
    #     response = transfer_ext_rp(inbound)
    # elif process == "storage_unit_ext_pr":
    #     response = storage_unit_ext_pr(inbound)
    # elif process == "transfer_ext":
    #     response = transfer_ext(inbound)
    # elif process == "transfer_EXT_confirmed":
    #     response = transfer_ext_confirmed(inbound)
    ##############Shipments##################
    elif process == "shipment_delivery":
        response = shipment_delivery(inbound)
    # ##############Vulcanized##################
    # elif process == "transfer_vul":
    #     response = transfer_vul(inbound)
    # elif process == "transfer_vul_confirmed":
    #     response = transfer_vul_confirmed(inbound)
    ##############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_cycle(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        # return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    ##############Control Cycle##################
    if process == "cycle_count_status":
        response = cycle_count_status(inbound)
    elif process == "cycle_count_transfer":
        response = cycle_count_transfer(inbound)
    ##############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_vul(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        # return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    ##############Vulcanized##################
    if process == "transfer_vul":
        response = transfer_vul(inbound)
    elif process == "transfer_vul_confirmed":
        response = transfer_vul_confirmed(inbound)
    ##############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_ext(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        # return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    ##############Extrusion##################
    if process == "handling_ext":
        response = handling_ext(inbound)
    elif process == "confirm_ext_hu":
        response = confirm_ext_hu(inbound)
    elif process == "transfer_ext_rp":
        response = transfer_ext_rp(inbound)
    elif process == "storage_unit_ext_pr":
        response = storage_unit_ext_pr(inbound)
    elif process == "transfer_ext":
        response = transfer_ext(inbound)
    elif process == "transfer_EXT_confirmed":
        response = transfer_ext_confirmed(inbound)
    ##############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response
#####################
# Inbound Functions
#####################


#####################
# Receiver Functions
#####################
def receiver_queue():
    current_queue = re.sub("receiver_", "", (inspect.stack()[0][3])).lower()

    def on_request(ch, method, props, body):
        global pika_body
        pika_body = body
        print(f"Request:    [{current_queue}] %s" % json.dumps(json.loads(body.decode(encoding="utf8"))))
        SAP_ErrorWindows.error_windows()

        try:
            threads_queue.put(props.reply_to)
            sap_login_queue.put(props.reply_to)
            sap_connections(current_queue)
        except Exception as err:
            error_logger(err)
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            os.system(f'taskkill /im "Monitor.exe"')

        insert_text(body.decode(encoding="utf8"))

        #######################################################
        con = threads_queue.unfinished_tasks - threads_queue.qsize()

        result_sap_alive = json.loads(SAP_Alive.Main())
        while True:
            if con in middle_list:
                if con == result_sap_alive["connections"] - 1:
                    con = 0
                else:
                    con += 1
            else:
                middle_list.append(con)
                break
        # print(f"[{current_queue}] unfinished", threads_queue.unfinished_tasks, "size", threads_queue.qsize(), "** CON", con, "list", middle_list)
        threads_queue.get()
        try:

            response = eval(f"process_inbound_{current_queue}")(con, body)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            insert_response_(response)
            print(f"Response:   [{current_queue}] %s" % str(response))
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=str(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as err:
            error_logger(err)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        #######################################################

    # params = pika.ConnectionParameters(heartbeat=600, blocked_connection_timeout=300)
    # connection = pika.BlockingConnection(params)
    # # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # channel = connection.channel()
    # channel.queue_declare(queue='rpc_queue', durable=True)
    # channel.basic_qos(prefetch_count=1)
    # channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
    # print(f" [{current_queue}] Awaiting RPC requests")
    # channel.start_consuming()

    try:
        params = pika.ConnectionParameters(heartbeat=900, blocked_connection_timeout=600)
        connection = pika.BlockingConnection(params)
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=f'rpc_{current_queue}', durable=True)
        channel.queue_declare(queue=f'rpc_{current_queue}_low', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=f'rpc_{current_queue}', on_message_callback=on_request)
        channel.basic_consume(queue=f'rpc_{current_queue}_low', on_message_callback=on_request)

        print(f"[{current_queue}] Awaiting RPC requests")

        mainWindow.list.insert(END, f' Res     [Success]:  Pika Connection Established {current_queue}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [success]:   Pika Connection Established {current_queue}'

        channel.start_consuming()
    except Exception as e:
        print(f"Exception:   [{current_queue}] %s" % str(e))
        error_logger(e)
        mainWindow.list.insert(END, f' Res     [Error]:  {e}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [Error]:   {e}'
        time.sleep(2)
        eval(f"receiver_{current_queue}")


def receiver_cycle():
    current_queue = re.sub("receiver_", "", (inspect.stack()[0][3])).lower()

    def on_request(ch, method, props, body):
        global pika_body
        pika_body = body
        print(f"Request:    [{current_queue}] %s" % json.dumps(json.loads(body.decode(encoding="utf8"))))
        SAP_ErrorWindows.error_windows()

        try:
            threads_queue.put(props.reply_to)
            sap_login_queue.put(props.reply_to)
            sap_connections(current_queue)
        except Exception as err:
            error_logger(err)
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            os.system(f'taskkill /im "Monitor.exe"')

        insert_text(body.decode(encoding="utf8"))

        #######################################################
        con = threads_queue.unfinished_tasks - threads_queue.qsize()

        result_sap_alive = json.loads(SAP_Alive.Main())
        while True:
            if con in middle_list:
                if con == result_sap_alive["connections"] - 1:
                    con = 0
                else:
                    con += 1
            else:
                middle_list.append(con)
                break
        # print(f"[{current_queue}] unfinished", threads_queue.unfinished_tasks, "size", threads_queue.qsize(), "** CON", con, "list", middle_list)
        threads_queue.get()
        try:

            response = eval(f"process_inbound_{current_queue}")(con, body)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            insert_response_(response)
            print(f"Response:   [{current_queue}] %s" % str(response))
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=str(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as err:
            error_logger(err)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        #######################################################

    # params = pika.ConnectionParameters(heartbeat=600, blocked_connection_timeout=300)
    # connection = pika.BlockingConnection(params)
    # # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # channel = connection.channel()
    # channel.queue_declare(queue='rpc_queue', durable=True)
    # channel.basic_qos(prefetch_count=1)
    # channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
    # print(f" [{current_queue}] Awaiting RPC requests")
    # channel.start_consuming()

    try:
        params = pika.ConnectionParameters(heartbeat=900, blocked_connection_timeout=600)
        connection = pika.BlockingConnection(params)
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=f'rpc_{current_queue}', durable=True)
        # channel.queue_declare(queue=f'rpc_{current_queue}_low', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=f'rpc_{current_queue}', on_message_callback=on_request)
        # channel.basic_consume(queue=f'rpc_{current_queue}_low', on_message_callback=on_request)

        print(f"[{current_queue}] Awaiting RPC requests")

        mainWindow.list.insert(END, f' Res     [Success]:  Pika Connection Established {current_queue}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [success]:   Pika Connection Established {current_queue}'

        channel.start_consuming()
    except Exception as e:
        print(f"Exception:   [{current_queue}] %s" % str(e))
        error_logger(e)
        mainWindow.list.insert(END, f' Res     [Error]:  {e}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [Error]:   {e}'
        time.sleep(2)
        eval(f"receiver_{current_queue}")


def receiver_vul():
    current_queue = re.sub("receiver_", "", (inspect.stack()[0][3])).lower()

    def on_request(ch, method, props, body):
        global pika_body
        pika_body = body
        print(f"Request:    [{current_queue}] %s" % json.dumps(json.loads(body.decode(encoding="utf8"))))
        SAP_ErrorWindows.error_windows()

        try:
            threads_queue.put(props.reply_to)
            sap_login_queue.put(props.reply_to)
            sap_connections(current_queue)
        except Exception as err:
            error_logger(err)
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            os.system(f'taskkill /im "Monitor.exe"')

        insert_text(body.decode(encoding="utf8"))

        #######################################################
        con = threads_queue.unfinished_tasks - threads_queue.qsize()

        result_sap_alive = json.loads(SAP_Alive.Main())
        while True:
            if con in middle_list:
                if con == result_sap_alive["connections"] - 1:
                    con = 0
                else:
                    con += 1
            else:
                middle_list.append(con)
                break
        # print(f"[{current_queue}] unfinished", threads_queue.unfinished_tasks, "size", threads_queue.qsize(), "** CON", con, "list", middle_list)
        threads_queue.get()
        try:

            response = eval(f"process_inbound_{current_queue}")(con, body)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            insert_response_(response)
            print(f"Response:   [{current_queue}] %s" % str(response))
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=str(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as err:
            error_logger(err)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        #######################################################

    # params = pika.ConnectionParameters(heartbeat=600, blocked_connection_timeout=300)
    # connection = pika.BlockingConnection(params)
    # # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # channel = connection.channel()
    # channel.queue_declare(queue='rpc_queue', durable=True)
    # channel.basic_qos(prefetch_count=1)
    # channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
    # print(f" [{current_queue}] Awaiting RPC requests")
    # channel.start_consuming()

    try:
        params = pika.ConnectionParameters(heartbeat=900, blocked_connection_timeout=600)
        connection = pika.BlockingConnection(params)
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=f'rpc_{current_queue}', durable=True)
        # channel.queue_declare(queue=f'rpc_{current_queue}_low', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=f'rpc_{current_queue}', on_message_callback=on_request)
        # channel.basic_consume(queue=f'rpc_{current_queue}_low', on_message_callback=on_request)

        print(f"[{current_queue}] Awaiting RPC requests")

        mainWindow.list.insert(END, f' Res     [Success]:  Pika Connection Established {current_queue}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [success]:   Pika Connection Established {current_queue}'

        channel.start_consuming()
    except Exception as e:
        print(f"Exception:   [{current_queue}] %s" % str(e))
        error_logger(e)
        mainWindow.list.insert(END, f' Res     [Error]:  {e}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [Error]:   {e}'
        time.sleep(2)
        eval(f"receiver_{current_queue}")


def receiver_ext():
    current_queue = re.sub("receiver_", "", (inspect.stack()[0][3])).lower()

    def on_request(ch, method, props, body):
        global pika_body
        pika_body = body
        print(f"Request:    [{current_queue}] %s" % json.dumps(json.loads(body.decode(encoding="utf8"))))
        SAP_ErrorWindows.error_windows()

        try:
            threads_queue.put(props.reply_to)
            sap_login_queue.put(props.reply_to)
            sap_connections(current_queue)
        except Exception as err:
            error_logger(err)
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            os.system(f'taskkill /im "Monitor.exe"')

        insert_text(body.decode(encoding="utf8"))

        #######################################################
        con = threads_queue.unfinished_tasks - threads_queue.qsize()

        result_sap_alive = json.loads(SAP_Alive.Main())
        while True:
            if con in middle_list:
                if con == result_sap_alive["connections"] - 1:
                    con = 0
                else:
                    con += 1
            else:
                middle_list.append(con)
                break
        # print(f"[{current_queue}] unfinished", threads_queue.unfinished_tasks, "size", threads_queue.qsize(), "** CON", con, "list", middle_list)
        threads_queue.get()
        try:

            response = eval(f"process_inbound_{current_queue}")(con, body)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            insert_response_(response)
            print(f"Response:   [{current_queue}] %s" % str(response))
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=str(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as err:
            error_logger(err)
            middle_list.remove(con)
            threads_queue.task_done()
            sap_login_queue.task_done()
            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        #######################################################

    # params = pika.ConnectionParameters(heartbeat=600, blocked_connection_timeout=300)
    # connection = pika.BlockingConnection(params)
    # # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # channel = connection.channel()
    # channel.queue_declare(queue='rpc_queue', durable=True)
    # channel.basic_qos(prefetch_count=1)
    # channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
    # print(f" [{current_queue}] Awaiting RPC requests")
    # channel.start_consuming()

    try:
        params = pika.ConnectionParameters(heartbeat=900, blocked_connection_timeout=600)
        connection = pika.BlockingConnection(params)
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=f'rpc_{current_queue}', durable=True)
        # channel.queue_declare(queue=f'rpc_{current_queue}_low', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=f'rpc_{current_queue}', on_message_callback=on_request)
        # channel.basic_consume(queue=f'rpc_{current_queue}_low', on_message_callback=on_request)

        print(f"[{current_queue}] Awaiting RPC requests")

        mainWindow.list.insert(END, f' Res     [Success]:  Pika Connection Established {current_queue}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [success]:   Pika Connection Established {current_queue}'

        channel.start_consuming()
    except Exception as e:
        print(f"Exception:   [{current_queue}] %s" % str(e))
        error_logger(e)
        mainWindow.list.insert(END, f' Res     [Error]:  {e}')
        mainWindow.list.see(END)
        label_text["text"] = f' Res     [Error]:   {e}'
        time.sleep(2)
        eval(f"receiver_{current_queue}")
#####################
# Receiver Functions
#####################


if __name__ == '__main__':
    master: Tk = Tk()
    master_top = Toplevel()
    mainWindow = window.MainApplication(master)
    secondaryWindow = window.SecondaryWindow(master, master_top)
    master_top.withdraw()

    mainWindow.list = Listbox(mainWindow.frame)
    mainWindow.list.configure(bg=mainWindow.background_color, foreground="white", highlightbackground=mainWindow.background_color)
    mainWindow.list.grid(row=7, column=0, padx=5, pady=5, sticky=E + W + N + S)
    master.protocol("WM_DELETE_WINDOW", quit_window)
    master.bind("<Unmap>", show_master_top)

    img = PhotoImage(file=r"./img/icon.png").subsample(5, 5)
    btn = Button(master_top, text='Monitor:', image=img, borderwidth=0, highlightthickness=0, command=close_secondary)
    btn.grid(row=0, column=0, padx=0, pady=15)
    btn.config(bg='#152532', fg='white')

    #####################
    # Global variables
    #####################
    label_text = Label(master_top, bg="#152532")
    label_text.configure(fg="#FCBD1E")
    label_text.grid(row=0, column=1, padx=5, pady=.5, sticky=W)
    current_process = ""
    pika_body = ""
    middle_list = []
    #####################
    # Global variables
    #####################

    threads_queue = queue.Queue()
    sap_login_queue = queue.Queue()

    receive_thread = Thread(target=receiver_queue)
    receive_thread_cycle = Thread(target=receiver_cycle)
    receive_thread_vul = Thread(target=receiver_vul)
    receive_thread_ext = Thread(target=receiver_ext)

    receive_thread.start()
    receive_thread_cycle.start()
    receive_thread_vul.start()
    receive_thread_ext.start()
    master.mainloop()
