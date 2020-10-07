<center><strong><h1>Python Monitor</h1></strong></center>


<p align="center">
  <img src="https://raw.githubusercontent.com/aramogs/Monitor/master/img/logo.png" width="50%"/>
</p>

<center><p>Program dedicated to receive requests and process them via SAPscript</p></center>
<center><p>Using RabbitMQ RPC protocol the Monitor receives and process requests from the clients</p></center>

### Prerequisites 

Required:  
- [Python](https://nodejs.org/) v3.6+.
- [RabbitMQ](https://www.rabbitmq.com/) v3.8+.

Optional:
- [Bartender](https://www.seagullscientific.com/software/) 11.09+.
- [MySQL](https://www.mysql.com/) v8.0+.
>Open a terminal in the root directory and run the following commands.

Note: For security reasons .env file is not included
```vbs
pip install -r requirements.txt
python .\Monitor.py
```

### .env structure
Required:
- SAP_USER=****
- SAP_PASS=****
- SAP_NAME=****

Optional:
- PRINT_SERVER=****
- BARTENDER_SERVER=****
- BARTENDER_PORT=****
- DB_USER=****
- DB_PASSWORD=****
- DB_HOST=****
- DB_CONFIG_NAME=****
- DB_PT_NAME=****

### Building Executable
>Open terminal in the root directory and run the following commands:

```vbs
pip install pyinstaller
python -m PyInstaller  .\Monitor.spec
```
>Go to the created folder "build" and double click Monitor.exe
