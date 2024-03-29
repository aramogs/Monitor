import inspect
import queue
import signal
import threading
import time
import tkinter.messagebox
import schedule
import pika
import window
# from threading import Thread
from tkinter import *

from functions import SAP_Count
from functions.CC.Functions import *  # Control Cycle
from functions.FG.Functions import *  # Finished Goods
from functions.PR.Functions import *  # Production
from functions.RM.Functions import *  # Raw Material
from functions.RW.Functions import *  # Re Work
from functions.SA.Functions import *  # Sub Assembly
from functions.SF.Functions import *  # Semi Finished
from functions.SH.Functions import *  # Shipments
from functions.EX.Functions import *  # Extrusion
from functions.VU.Functions import *  # Vulcanized
from functions.PI.Functions import *  # PA Pipes


#####################
# Window Functions
#####################
def quit_window():
    os.kill(os.getpid(), signal.SIGTERM)


def show_master_top(es):
    master_top.deiconify()
    master.withdraw()


def close_secondary():
    master.deiconify()
    master_top.withdraw()


def insert_text(request):
    inbound = json.loads(request)
    global label_text
    try:
        process = inbound["process"]
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

    if inbound["error"] == "N/A" or inbound["error"][0] == "N/A":
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
        exc_info=True)  # Con esto se genera log
    logging.error(f'END - ########################################################################################')
    # os.system(f' taskkill /im "Monitor.exe"')


def sap_connections(current_queue):
    qsize = sap_login_queue.qsize()
    sap_login_queue.get()
    result_sap_count = json.loads(SAP_Count.main())
    if result_sap_count["sap_status"] == "error" or result_sap_count["connections"] < sap_login_queue.unfinished_tasks:
        print(f"[{current_queue}] Error SAP Connection Down")
        sap_login()
        if json.loads(SAP_Count.main())["connections"] < qsize:
            sap_connections(current_queue)


#####################
# Inbound Functions
#####################
def process_inbound_queue(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Raw Material##################
    # if process == "partial_transfer":
    #     response = partial_transfer(inbound)
    # elif process == "partial_transfer_confirmed":
    #     response = partial_transfer_confirmed(inbound)
    # elif process == "transfer_mp_confirmed":
    #     response = transfer_mp_confirmed(inbound)
    # elif process == "raw_delivery_verify":
    #     response = raw_delivery_verify(inbound)
    # elif process == "raw_fifo_verify":
    #     response = raw_fifo_verify(inbound)
    # elif process == "raw_mp_confirmed":
    #     response = raw_mp_confirmed(inbound)
    # elif process == "raw_mp_confirmed_v":
    #     response = raw_mp_confirmed_v(inbound)
    # elif process == "location_mp_material":
    #     response = location_mp_material(inbound)
    # elif process == "location_mp_serial":
    #     response = location_mp_serial(inbound)
    # #############Finished Goods##################
    # elif process == "transfer_fg":
    #     response = transfer_fg(inbound)
    # elif process == "transfer_fg_confirmed":
    #     response = transfer_fg_confirmed(inbound)
    # elif process == "master_fg_gm_verify":
    #     response = master_fg_gm_verify(inbound)
    # elif process == "master_fg_gm_create":
    #     response = master_fg_gm_create(inbound)
    # #############Sub Assembly##################
    # if process == "transfer_sa":
    #     response = transfer_sa(inbound)
    # elif process == "transfer_sa_return":
    #     response = transfer_sa_return(inbound)
    # elif process == "reprint_sa":
    #     response = reprint_sa(inbound)
    # ##############Semi Finished##################
    # elif process == "handling_sf":
    #     response = handling_sf(inbound)
    # elif process == "transfer_sf":
    #     response = transfer_sf(inbound)
    # elif process == "transfer_sfr":
    #     response = transfer_sfr(inbound)
    # elif process == "transfer_sfr_return":
    #     response = transfer_sfr_return(inbound)
    # elif process == "reprint_sf":
    #     response = reprint_sf(inbound)
    # ##############Re Work##################
    # elif process == "transfer_rework_in":
    #     response = transfer_rework_in(inbound)
    # elif process == "transfer_rework_out":
    #     response = transfer_rework_out(inbound)
    # #############Production##################
    if process == "create_pr_hu":
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
    elif process == "create_mes_pr_hu":
        response = create_mes_pr_hu(inbound)
    # ##############Shipments##################
    # elif process == "shipment_delivery":
    #     response = shipment_delivery(inbound)
    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_fg(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Finished Goods##################
    if process == "transfer_fg":
        response = transfer_fg(inbound)
    elif process == "transfer_fg_confirmed":
        response = transfer_fg_confirmed(inbound)
    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_fg_gm(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Master GM##################
    if process == "master_fg_gm_verify":
        response = master_fg_gm_verify(inbound)
    elif process == "master_fg_gm_create":
        response = master_fg_gm_create(inbound)

    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_rm(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Raw Material##################
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

    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_ship(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        # return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Shipments##################
    if process == "shipment_delivery":
        response = shipment_delivery(inbound)
    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_cycle(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        inbound["storage_location"] = ""
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Control Cycle##################
    if process == "cycle_count_status":
        response = cycle_count_status(inbound)
    elif process == "cycle_count_transfer":
        response = cycle_count_transfer(inbound)
    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_rw(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])

    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Re Work##################
    if process == "transfer_rework_in":
        response = transfer_rework_in(inbound)
    elif process == "transfer_rework_out":
        response = transfer_rework_out(inbound)
    # ############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_vul(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Vulcanized Transfers##################
    if process == "transfer_vul_serial":
        response = transfer_vul_serial(inbound)
    elif process == "transfer_vul_material":
        response = transfer_vul_material(inbound)
    elif process == "transfer_vul_mandrel":
        response = transfer_vul_mandrel(inbound)
    elif process == "transfer_vul_confirmed":
        response = transfer_vul_confirmed(inbound)
    elif process == "audit_ext":
        response = audit_ext(inbound)
    # #############Vulcanized##################
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
    elif process == "reprint_sfr":
        response = reprint_sfr(inbound)

    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_sa(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Sub Assembly##################
    if process == "handling_sa":
        response = handling_sa(inbound)
    elif process == "transfer_sa":
        response = transfer_sa(inbound)
    elif process == "reprint_sa":
        response = reprint_sa(inbound)

    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_pip(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############PA Pipes Transfers##################
    if process == "transfer_pip":
        response = transfer_pip(inbound)
    elif process == "transfer_pip_confirmed":
        response = transfer_pip_confirmed(inbound)
    elif process == "audit_pip":
        response = audit_pip(inbound)
    # #############PA Pipes##################
    elif process == "handling_pip":
        response = handling_pip(inbound)
    elif process == "transfer_pip":
        response = transfer_pip(inbound)
    elif process == "transfer_pipr":
        response = transfer_pipr(inbound)
    elif process == "transfer_pipr_return":
        response = transfer_pipr_return(inbound)
    elif process == "reprint_pip":
        response = reprint_pip(inbound)
    elif process == "reprint_pipr":
        response = reprint_pipr(inbound)

    # #############_NO_PROCESS_##################
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

    # #############Extrusion##################
    if process == "confirm_ext_hu":
        response = confirm_ext_hu(inbound)
    elif process == "transfer_ext_rp":
        response = transfer_ext_rp(inbound)
    elif process == "storage_unit_ext_pr":
        response = storage_unit_ext_pr(inbound)
    elif process == "transfer_ext_mandrel":
        response = transfer_ext_mandrel(inbound)
    elif process == "transfer_ext_serial":
        response = transfer_ext_serial(inbound)
    elif process == "transfer_EXT_confirmed":
        response = transfer_ext_confirmed(inbound)
    elif process == "verify_rubber":
        response = verify_rubber(inbound)
    # #############_NO_PROCESS_##################
    else:
        current_queue = inspect.stack()[0][3]
        response = json.dumps({"error": f'invalid_process: {process} for: {current_queue}'})
    return response


def process_inbound_ext_labels(con, body):
    inbound = json.loads(body.decode(encoding="utf8"))
    storage_location = DB.select_storage_location(inbound["station"])
    if len(storage_location) == 0:
        return json.dumps({"error": f'Device not allowed: {inbound["station"]}'})
        pass
    else:
        inbound["storage_location"] = storage_location[0][0]
    inbound["con"] = con
    process = inbound["process"]

    # #############Extrusion Labels##################
    if process == "handling_ext":
        response = handling_ext(inbound)
    # #############_NO_PROCESS_##################
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

class ReceiverFunctions(threading.Thread):

    def __init__(self, thread_name):
        threading.Thread.__init__(self)
        self.thread_name = thread_name

    def run(self):

        # current_queue = re.sub("receiver_", "", (inspect.stack()[0][3])).lower()
        current_queue = self.thread_name

        def on_request(ch, method, props, body):
            global pika_body
            pika_body = body
            print(f"Request:    [{current_queue}] %s" % json.loads(json.dumps(body.decode(encoding="UTF8"))))
            SAP_ErrorWindows.error_windows()

            try:
                threads_queue.put(props.reply_to)
                sap_login_queue.put(props.reply_to)
                sap_connections(current_queue)
            except Exception as err:
                error_logger(err)
                ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                os.system(f'taskkill /im "Monitor.exe"')

            insert_text(body.decode(encoding="utf8"))

            #######################################################
            con = threads_queue.unfinished_tasks - threads_queue.qsize()

            result_sap_alive = json.loads(SAP_Count.main())
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
                ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=str(json.dumps({"serial": "N/A", "error": f'{err}'})))
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
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=f'rpc_{current_queue}', on_message_callback=on_request)
            print(f"[{current_queue}] Awaiting RPC requests")
            mainWindow.list.insert(END, f' Res     [Success]:  Pika Connection Established {current_queue}')
            mainWindow.list.see(END)
            label_text["text"] = f' Res     [success]:   Pika Connection Established {current_queue}'

            if self.thread_name == "queue":
                channel.queue_declare(queue=f'rpc_{current_queue}_low', durable=True)
                channel.basic_consume(queue=f'rpc_{current_queue}_low', on_message_callback=on_request)
                print(f"[{current_queue}_low] Awaiting RPC requests")
                mainWindow.list.insert(END, f' Res     [Success]:  Pika Connection Established {current_queue}_low')
                mainWindow.list.see(END)
                label_text["text"] = f' Res     [success]:   Pika Connection Established {current_queue}_low'

            channel.start_consuming()
        except Exception as err_:
            print(f"Exception:   [{current_queue}] %s" % str(err_))
            error_logger(err_)
            mainWindow.list.insert(END, f' Res     [Error]:  {err_}')
            mainWindow.list.see(END)
            label_text["text"] = f' Res     [Error]:   {err_}'
            time.sleep(2)
            # eval(f"receiver_{current_queue}")
#####################
# Receiver Functions
#####################


def sap_alive_loop():
    while True:
        result_alive = json.loads(SAP_Alive.main())
        if result_alive["sap_status"] == "error":
            insert_text(json.dumps({"status": "ERROR", "process": "SAP_ALIVE"}))
        else:
            insert_text(json.dumps({"status": "OK", "process": "SAP_ALIVE"}))
        threading.Event().wait(60)


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

    #####################
    # Beginning Threads
    #####################
    sap_alive_thread = threading.Thread(target=sap_alive_loop, daemon=True)
    sap_alive_thread.start()

    if not json.loads(f'{os.getenv("THREADS")}'):
        tkinter.messagebox.showerror("No Threads", "No threads check .env file")
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        for th in json.loads(f'{os.getenv("THREADS")}'):
            try:
                ReceiverFunctions(th).setDaemon(True)
                ReceiverFunctions(th).start()
            except Exception as e:
                tkinter.messagebox.showerror("Incorrect Thread", f'{e}')
                os.kill(os.getpid(), signal.SIGTERM)

    master.mainloop()
