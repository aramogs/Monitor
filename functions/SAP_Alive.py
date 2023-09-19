import multiprocessing
import win32com.client
import os
import json
import pythoncom
import time
import schedule
from functions import SAP_Login


def get_sapgui():
    pythoncom.CoInitialize()
    return win32com.client.GetObject("SAPGUI")



def main():
    try:
        sapgui_process = multiprocessing.Process(target=get_sapgui)
        sapgui_process.start()
        sapgui_process.join(timeout=30)

        if sapgui_process.is_alive():
            sapgui_process.terminate()
            sapgui_process.join()  # Wait for the termination to complete

        if sapgui_process.exitcode != 0:
            # print("SAPGUI retrieval process failed.")
            os.system(f'taskkill /f /im "Monitor.exe"')
            os.system(f'taskkill /f /im "saplogon.exe"')
            SAP_Login.Main()
            response = {"sap_status": "error", "connections": 0}
            return json.dumps(response)
        else:
            pythoncom.CoInitialize()
            SapGuiAuto = get_sapgui()
            application = SapGuiAuto.GetScriptingEngine
            # print("SAPGUI retrieved successfully.")
            response = {"sap_status": "ok", "connections": len(application.Children)}
            return json.dumps(response)
            # Your code to work with SAPGUI goes here
    except Exception as e:
        # Handle other exceptions if needed
        print(f"An error occurred: {e}")


def job():
    result = main()
    print(result)


if __name__ == "__main__":
    # Schedule the job to run every minute
    schedule.every(1).minutes.do(job)

    # Run the job continuously
    while True:
        schedule.run_pending()
        time.sleep(1)
