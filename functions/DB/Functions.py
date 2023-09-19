import datetime
import os
import logging
import mysql.connector
import redis
from dotenv import load_dotenv

load_dotenv()


def logger(e):
    now = datetime.datetime.now()
    error_time = now.strftime("%Y-%m-%d_%H-%M")
    logging.basicConfig(filename='.\\logs\\error_{}.log'.format(error_time), filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.error(
        f'START - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nJSON: {"DB-ERROR"}\nERROR: {e}',
        exc_info=True)  # Con esto se logea
    logging.error(f'END - !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


b10_config = {
    'user': f'{os.getenv("DB_USER")}',
    'password': f'{os.getenv("DB_PASSWORD")}',
    'host': f'{os.getenv("DB_HOST")}',
    'database': f'{os.getenv("DB_CONFIG_NAME")}',
    'raise_on_warnings': True
}

b10_bartender_config = {
    'user': f'{os.getenv("DB_USER")}',
    'password': f'{os.getenv("DB_PASSWORD")}',
    'host': f'{os.getenv("DB_HOST")}',
    'database': f'{os.getenv("DB_BARTENDER_NAME")}',
    'raise_on_warnings': True
}

b10_bartender_config_EX = {
    'user': f'{os.getenv("DB_USER_EX")}',
    'password': f'{os.getenv("DB_PASSWORD_EX")}',
    'host': f'{os.getenv("DB_HOST_EX")}',
    'database': f'{os.getenv("DB_BARTENDER_NAME_EX")}',
    'auth_plugin': 'mysql_native_password',
    'raise_on_warnings': True
}

warehouse_config = {
    'user': f'{os.getenv("DB_USER")}',
    'password': f'{os.getenv("DB_PASSWORD")}',
    'host': f'{os.getenv("DB_HOST")}',
    'database': f'{os.getenv("DB_PT_NAME")}',
    'raise_on_warnings': True
}

extrusion_config = {
    'user': f'{os.getenv("DB_EX_USER")}',
    'password': f'{os.getenv("DB_EX_PASSWORD")}',
    'host': f'{os.getenv("DB_EX_HOST")}',
    'database': f'{os.getenv("DB_EX_NAME")}',
    'auth_plugin': 'mysql_native_password',
    'raise_on_warnings': True
}

shipment_config = {
    'user': f'{os.getenv("DB_SHIPMENT_USER")}',
    'password': f'{os.getenv("DB_SHIPMENT_PASSWORD")}',
    'host': f'{os.getenv("DB_SHIPMENT_HOST")}',
    'database': f'{os.getenv("DB_SHIPMENT_NAME")}',
    'raise_on_warnings': True
}

redis_config = redis.Redis(
    host=os.getenv("DB_REDIS_SERVER"),
    port=6379,
    db=0
    )


class DB:
    @staticmethod
    def get_printer(station):
        """
        Function to get the printer information from the station id
        """
        try:
            db = mysql.connector.connect(**b10_config)
            query = f'SELECT impre FROM b10.station_conf WHERE no_estacion = "{station}"'
            cursor = db.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            db.close()
            return result[0][0]
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def insert_partial_transfer(emp_num, part_num, no_serie, linea, transfer_order):
        """
        Function to insert information about transfer order
        """
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = f'INSERT INTO partial_transfer (emp_num, part_num, no_serie, linea, transfer_order) ' \
                    f'VALUES ({emp_num}, "{part_num}", {no_serie}, "{linea}", {transfer_order})'

            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def insert_complete_transfer(emp_num, no_serie, result, area, storage_bin):
        """
        Function to insert information about transfer order
        """
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = f'INSERT INTO complete_transfer (emp_num, no_serie, result, area, storage_bin) ' \
                    f'VALUES ({emp_num}, {no_serie}, "{result}", "{area}", "{storage_bin}")'
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def insert_master_transfer(emp_num, part_num, no_serie_uc, no_serie_um, transfer_order):
        """
        Function to insert information about transfer order
        """
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = f'INSERT INTO master_transfer (emp_num,part_num, no_serie_uc,no_serie_um,transfer_order) ' \
                    f'VALUES ({emp_num}, "{part_num}", {no_serie_uc}, {no_serie_um}, {transfer_order})'
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_tables():
        """
        Function to get table names from database
        """
        try:
            db = mysql.connector.connect(**b10_bartender_config)
            query = f'SELECT table_name FROM information_schema.tables WHERE table_schema = "{os.getenv("DB_BARTENDER_NAME")}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_tables_ext():
        """
        Function to get table names from database
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'SELECT table_name FROM information_schema.tables WHERE table_schema = "{os.getenv("DB_BARTENDER_NAME")}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_printer(estacion):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**b10_config)
            query = f'SELECT impre FROM station_conf WHERE no_estacion = "{estacion}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    def select_printer_bartender(estacion):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**b10_config)
            query = f'SELECT impre_alt FROM station_conf WHERE no_estacion = "{estacion}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_alt_printer(estacion):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**b10_config)
            query = f'SELECT impre_alt FROM station_conf WHERE no_estacion = "{estacion}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def search_union(no_sap):
        """
        Function to find material number and all of its information in multiple tables
        """
        tables = DB.select_tables()
        for table in tables:
            db = mysql.connector.connect(**b10_bartender_config)
            query = f'SELECT * FROM {table[0]} WHERE no_sap = "{no_sap}"'

            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            values = cursor.fetchall()
            if len(values) != 0:
                try:
                    db = mysql.connector.connect(**b10_bartender_config)
                    query = f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="{os.getenv("DB_BARTENDER_NAME")}" AND TABLE_NAME="{table[0]}";'
                    cursor2 = db.cursor(buffered=True)
                    cursor2.execute(query)
                    db.commit()
                    db.close()
                    columns = cursor2.fetchall()
                    # print("Columnas", columns)
                    # print("Valores", values)
                    return columns, values[0], table[0]
                except Exception as e:
                    logger(e)
                    # print(e)

    @staticmethod
    def client_part_number(no_sap):
        """
        Function to find material number and all of its information in multiple tables
        """
        tables = DB.select_tables()
        for table in tables:
            db = mysql.connector.connect(**b10_bartender_config)
            query = f'SELECT cust_part FROM {table[0]} WHERE no_sap = "{no_sap}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            values = cursor.fetchall()

            if len(values) != 0:
                try:
                    db = mysql.connector.connect(**b10_bartender_config)
                    query = f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="{os.getenv("DB_BARTENDER_NAME")}" AND TABLE_NAME="{table[0]}";'
                    cursor2 = db.cursor(buffered=True)
                    cursor2.execute(query)
                    db.commit()
                    db.close()
                    columns = cursor2.fetchall()
                    # print("Columnas", columns)
                    # print("Valores", values)
                    return values[0]
                except Exception as e:
                    print("DB-Error:   [x] %s" % str(e))
                    logger(e)
                    pass

    @staticmethod
    def insert_cycle_transfer(storage_type, storage_bin, storage_unit, emp_num, status, sap_result):
        """
        Function to insert information about transfer order related to cycle count
        """
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = f'INSERT INTO cycle_count (storage_type, storage_bin, storage_unit, emp_num, status, sap_result) ' \
                    f'VALUES ("{storage_type}", "{storage_bin}", "{storage_unit}", "{emp_num}", "{status}", "{sap_result}")'

            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def insert_raw_delivery(values):
        """
        Function to insert information about transfer order
        """
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = f'INSERT INTO raw_delivery (numero_sap, descripcion_sap, contenedores, sup_name, turno, status) VALUES (%s, %s, %s, %s, %s, %s)'
            cursor = db.cursor()
            cursor.executemany(query, values)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def insert_raw_movement(raw_id, storage_type, emp_num, no_serie, result):
        """
        Function to insert information about transfer order
        """
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = f'INSERT INTO raw_movement (raw_id, storage_type, emp_num, no_serie, sap_result) ' \
                    f'VALUES ("{raw_id}", "{storage_type}", {emp_num}, {no_serie}, "{result}")'
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def update_ex_backflush(result_acred, serial_num, user_id):
        """
        Function to Update Extrusion labels successfully back flushed
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'UPDATE extrusion_labels SET status="Acreditado", result_acred="{result_acred}", emp_acred={user_id} WHERE serial={serial_num}'
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def update_ex_backflush_error(error, serial_num, user_id):
        """
        Function to Update Extrusion labels with errors at back flushed
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'UPDATE extrusion_labels SET result_acred="{error}", emp_acred={user_id} WHERE serial={serial_num}'
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_printer_ext(linea):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'SELECT printer FROM extrusion_conf WHERE linea = "{linea}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def update_plan_ext(plan_id):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'UPDATE production_plan SET status = "Impreso" WHERE plan_id = "{plan_id}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            # print(cursor.rowcount)
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def update_print_ext_return(serial_num, result):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'UPDATE extrusion_labels SET result_return = "{result}" WHERE serial = "{serial_num}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            # return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def update_print_ext(serial_num, plan_id, material, emp_num, cantidad, impresoType):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'INSERT INTO extrusion_labels (serial, plan_id, numero_parte, emp_num, cantidad, status) VALUES({serial_num},"{plan_id}", "{material}", {emp_num}, {cantidad}, "{impresoType}")'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            # return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def acred_print_ext(serial_num, result_acred, emp_num):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'UPDATE extrusion_labels SET status = "Acreditado", result_acred = "{result_acred}", emp_acred = "{emp_num}" WHERE serial = "{serial_num}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            # return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def acred_print_error_ext(serial_num, result_acred, emp_num):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'UPDATE extrusion_labels SET status = "Impreso", result_acred = "{result_acred}", emp_acred = "{emp_num}" WHERE serial = "{serial_num}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            # return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def transfer_print_ext(serial_num, result_transfer, emp_transfer):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'UPDATE extrusion_labels SET status = "Transferido", result_transfer = "{result_transfer}", emp_transfer = "{emp_transfer}" WHERE serial = "{serial_num}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            # return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def search_union_ext(no_sap):
        """
        Function to find material number and all of its information in multiple tables
        """
        tables = DB.select_tables_ext()
        for table in tables:
            db = mysql.connector.connect(**b10_bartender_config_EX)
            query = f'SELECT * FROM {table[0]} WHERE no_sap = "{no_sap}"'
            cursor = db.cursor(buffered=True)
            try:
                cursor.execute(query)
            except Exception as e:
                print(e)

            db.commit()
            db.close()
            values = cursor.fetchall()
            if len(values) != 0:
                try:
                    db = mysql.connector.connect(**extrusion_config)
                    query = f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="{os.getenv("DB_BARTENDER_NAME")}" AND TABLE_NAME="{table[0]}" ORDER BY ORDINAL_POSITION;'
                    cursor2 = db.cursor(buffered=True)
                    cursor2.execute(query)
                    db.commit()
                    db.close()
                    columns = cursor2.fetchall()
                    # print("Columnas", columns)
                    # print("Valores", values)
                    return columns, values[0], table[0]
                except Exception as e:
                    logger(e)
                    print(e)

    @staticmethod
    def update_ext_supply(material, material_description, extruder, quantity, operator_id, serial_num, sap_result):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**extrusion_config)
            query = f'INSERT INTO extrusion_supply (material, material_description, extruder, quantity, operator_id, serial_num, sap_result) ' \
                    f'VALUES("{material}","{material_description}", {extruder}, "{quantity}", {operator_id}, {serial_num}, "{sap_result}")'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            # return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass


    @staticmethod
    def insert_shipment_delivery(values_list):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**shipment_config)
            query = 'INSERT INTO embarque_delivery (delivery_embarque, delivery_delivery, delivery_master, delivery_single) VALUES(%s, %s, %s, %s)'
            cursor = db.cursor()
            cursor.executemany(query, values_list)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_shipment_delivery(delivery):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**shipment_config)
            query = f'SELECT DISTINCT delivery_delivery FROM embarque_delivery WHERE delivery_delivery = "{delivery}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_storage_location(estacion):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**b10_config)
            query = f'SELECT storage_location FROM station_conf WHERE no_estacion = "{estacion}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def select_product_version(estacion):
        """
        Function to get printer from station id
        """
        try:
            db = mysql.connector.connect(**b10_config)
            query = f'SELECT product_version FROM station_conf WHERE no_estacion = "{estacion}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def insert_audit_ext(serial_num, user_id, sap_num, part_description, sap_result):
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = 'INSERT INTO audit_ext (serial_num, user_id, sap_num, part_description, sap_result) ' \
                    f'VALUES({serial_num}, {user_id}, "{sap_num}", "{part_description}", "{sap_result}")'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass


class DBR:
    @staticmethod
    def set_hash(redis_hash, serial_num):
        try:
            redis_config.set(redis_hash, f'{serial_num}', 180)
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def update_hash(redis_hash, serial_num):
        try:
            redis_config.append(redis_hash, f'\n{serial_num}')
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass

    @staticmethod
    def get_hash(redis_hash):
        try:
            return redis_config.get(redis_hash)
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
            logger(e)
            pass
