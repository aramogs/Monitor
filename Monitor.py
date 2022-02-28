import signal
from threading import Thread
from tkinter import *

import pika
import time
import window
import logging

from functions.FG.Functions import *  # Finished Goods
from functions.RM.Functions import *  # Raw Material
from functions.SA.Functions import *  # Sub Assembly
from functions.SF.Functions import *  # Semi Finished
from functions.RW.Functions import *  # Re Work
from functions.PR.Functions import *  # Production
from functions.CC.Functions import *  # Control Cycle
from functions.SH.Functions import *  # Shipments


def quit_window():
    os.kill(os.getpid(), signal.SIGTERM)


def show_master_top(event):
    masterTop.deiconify()
    master.withdraw()


def close_secondary():
    master.deiconify()
    masterTop.withdraw()

try:
    master: Tk = Tk()
    masterTop = Toplevel()
    mainWindow = window.MainApplication(master)
    secondaryWindow = window.SecondaryWindow(master, masterTop)
    masterTop.withdraw()

    mainWindow._list = Listbox(mainWindow._frame)
    mainWindow._list.configure(bg=mainWindow._background_color, foreground="white")
    mainWindow._list.grid(row=7, column=0, padx=5, pady=5, sticky=E + W + N + S)
    master.protocol("WM_DELETE_WINDOW", quit_window)
    master.bind("<Unmap>", show_master_top)

    img = PhotoImage(file=r"./img/icon.png").subsample(5, 5)
    btn = Button(masterTop, text='Monitor:', image=img, borderwidth=0, highlightthickness=0, command=close_secondary)
    btn.grid(row=0, column=0, padx=0, pady=15)
    btn.config(bg='#152532', fg='white')
except Exception as e:
    print(e)

#####################
# Global variables
#####################
label_text = Label(masterTop, bg="#152532")
label_text.configure(fg="#FCBD1E")
label_text.grid(row=0, column=1, padx=5, pady=.5, sticky=W)
current_process = ""
pika_body = ""
#####################
# Global variables
#####################


def process_inbound(body):
    inbound = json.loads(body.decode(encoding="utf8"))
    process = inbound["process"]
    global current_process
    current_process = process

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
    elif process == "cycle_count_status":
        response = cycle_count_status(inbound)
    elif process == "cycle_count_transfer":
        response = cycle_count_transfer(inbound)
    ##############Extrusion##################
    elif process == "handling_ext":
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
    ##############Shipments##################
    elif process == "shipment_delivery":
        response = shipment_delivery(inbound)
    ##############_NO_PROCESS_##################
    else:
        response = json.dumps({"error": f'invalid_process: {process}'})
    return response


def insert_text(request):
    inbound = json.loads(request)
    try:
        station = inbound["station"]
        serial_num = inbound["serial_num"]
        material = inbound["material"]
        quantity = inbound["cantidad"]
        process = inbound["process"]
        global label_text
        if len(station) > 5:
            station = "WEB"

        mainWindow._list.insert(END,f' Req    [{process.capitalize()}] St: {station}  S/N: {serial_num}  SAP: {material}  Q: {quantity}')
        mainWindow._list.see(END)
        label_text["text"] = f' Req    [{process.capitalize()}] St: {station}  S/N: {serial_num}  SAP: {material}  Q: {quantity}'
        masterTop.lift()
    except KeyError:
        mainWindow._list.insert(END, f' Req    [Err] VERIFY JSON')
        mainWindow._list.see(END)
        label_text["text"] = f' Req    [Err] VERIFY JSON'


def insert_response(response):
    inbound = json.loads(response)
    global label_text
    global current_process

    lists = {
        "process1": ["partial_transfer", "partial_transfer_confirmed"],
        "process2": ["handling_sf", "transfer_sa", "transfer_sa_return", "transfer_sfr", "transfer_sfr_return", "reprint_sa", "reprint_sf", "transfer_sf", "transfer_rework_in",
                     "transfer_rework_out", "create_pr_hu", "confirm_pr_hu", "no_confirm_pr_hu", "create_alternate_pr_hu", "create_pr_hu_del", "create_pr_hu_wm"],
        "process3": ["transfer_fg", "transfer_fg_confirmed", "transfer_mp_confirmed", "master_fg_gm_verify", "confirm_ext_hu", "transfer_ext_rp", "cycle_count_status",
                     "raw_delivery_verify", "shipment_delivery"]
    }
    match = False
    for li, processes in lists.items():
        for process in processes:
            if process == current_process:
                match = True

                if li == "process1":
                    serial = inbound["serial"]
                    material = inbound["material"]
                    quantity = inbound["cantidad"]
                    error = inbound["error"]

                    if error == "N/A":
                        mainWindow._list.insert(END, f' Res     [Success]: S/N: {serial} SAP: {material} Q: {quantity}')
                        mainWindow._list.see(END)
                        label_text["text"] = f' Res     [Success]: S/N: {serial} SAP: {material} Q: {quantity}'
                        masterTop.lift()
                    else:
                        mainWindow._list.insert(END, f' Res     [Error]:   S/N: {serial} Err: {error}')
                        mainWindow._list.see(END)
                        label_text["text"] = f' Res     [Error]:   S/N: {serial} Err: {error}'
                        masterTop.lift()

                if li == "process2":
                    result = inbound["result"]
                    serial = inbound["serial"]
                    error = inbound["error"]

                    if error == "N/A":
                        mainWindow._list.insert(END, f' Res     [Success]: S/N: {serial} Result: {result}')
                        mainWindow._list.see(END)
                        label_text["text"] = f' Res     [Success]: S/N: {serial} Result: {result}'
                        masterTop.lift()
                    else:
                        mainWindow._list.insert(END, f' Res     [Error]:   S/N: {serial} Err: {error}')
                        mainWindow._list.see(END)
                        label_text["text"] = f' Res     [Error]:   S/N: {serial} Err: {error}'
                        masterTop.lift()

                if li == "process3":
                    error = inbound["error"]
                    if error == "N/A":
                        mainWindow._list.insert(END, f' Res     [Success]:  Proceso terminado')
                        mainWindow._list.see(END)
                        label_text["text"] = f' Res     [Success]:   Proceso terminado'
                        masterTop.lift()
                    else:
                        mainWindow._list.insert(END, f' Res     [Error]:  {inbound["error"]}')
                        mainWindow._list.see(END)
                        label_text["text"] = f' Res     [Success]:   {inbound["error"]}'
                        masterTop.lift()
    if not match:
        mainWindow._list.insert(END, f' Res     [Error]:  {inbound["error"]}')
        mainWindow._list.see(END)
        label_text["text"] = f' Res     [Error]:   {inbound["error"]}'
        masterTop.lift()


def sap_login():
    if json.loads(SAP_Alive.Main())["sap_status"] == "error":
        print("Error - SAP Connection Down")
        if json.loads(SAP_Login.Main())["sap_status"] != "ok":
            sap_login()
    else:
        # print("Success - SAP Connection Up")
        pass


def receiver():
    def on_request(ch, method, props, body):
        global pika_body
        pika_body = body
        print("Request:    [x] %s" % body.decode(encoding="utf8"))
        SAP_ErrorWindows.error_windows()

        try:
            sap_login()
        except Exception as err:
            now = datetime.datetime.now()
            error_time = now.strftime("%Y-%m-%d_%H-%M")
            logging.basicConfig(filename='.\\logs\\error_{}.log'.format(error_time), filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logging.error(f'START - ########################################################################################\nJSON: {pika_body.decode(encoding="utf8")}\nERROR: {err}', exc_info=True)  # Con esto se logea
            logging.error(f'END - ########################################################################################')
            os.system(f'taskkill /im "Monitor.exe"')

        insert_text(body.decode(encoding="utf8"))
        response = process_inbound(body)
        insert_response(response)

        print("Response:   [x] %s" % str(response))
        ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # params = pika.ConnectionParameters(heartbeat=600, blocked_connection_timeout=300)
    # connection = pika.BlockingConnection(params)
    # # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # channel = connection.channel()
    # channel.queue_declare(queue='rpc_queue', durable=True)
    # channel.basic_qos(prefetch_count=1)
    # channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
    # print(" [x] Awaiting RPC requests")
    # channel.start_consuming()

    try:
        params = pika.ConnectionParameters(heartbeat=900, blocked_connection_timeout=600)
        connection = pika.BlockingConnection(params)
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='rpc_queue', durable=True)
        channel.queue_declare(queue='rpc_queue_low', durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)
        channel.basic_consume(queue='rpc_queue_low', on_message_callback=on_request)

        print(" [x] Awaiting RPC requests")

        mainWindow._list.insert(END, f' Res     [Success]:  Pika Connection Established')
        mainWindow._list.see(END)
        label_text["text"] = f' Res     [success]:   Pika Connection Established'

        channel.start_consuming()
    except Exception as e:
        print("Exception:   [x] %s" % str(e))

        now = datetime.datetime.now()
        error_time = now.strftime("%Y-%m-%d_%H-%M")

        logging.basicConfig(filename='.\\logs\\error_{}.log'.format(error_time), filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.error(f'START - ########################################################################################\nJSON: {pika_body.decode(encoding="utf8")}\nERROR: {e}', exc_info=True)  # Con esto se logea
        logging.error(f'END - ########################################################################################')

        mainWindow._list.insert(END, f' Res     [Error]:  {e}')
        mainWindow._list.see(END)
        label_text["text"] = f' Res     [Error]:   {e}'

        time.sleep(2)
        receiver()


receive_thread = Thread(target=receiver)
receive_thread.start()
master.mainloop()
