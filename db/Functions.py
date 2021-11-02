import os
import mysql.connector

from dotenv import load_dotenv

load_dotenv()

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
            pass

    @staticmethod
    def insert_complete_transfer(emp_num, no_serie, result, area):
        """
        Function to insert information about transfer order
        """
        try:
            db = mysql.connector.connect(**warehouse_config)
            query = f'INSERT INTO complete_transfer (emp_num, no_serie, result, area) ' \
                    f'VALUES ({emp_num}, {no_serie}, "{result}", "{area}")'
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.rowcount
        except Exception as e:
            print("DB-Error:   [x] %s" % str(e))
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
            pass

    @staticmethod
    def select_tables():
        """
        Function to get table names from database
        """
        db = mysql.connector.connect(**b10_bartender_config)
        query = f'SELECT table_name FROM information_schema.tables WHERE table_schema = "{os.getenv("DB_BARTENDER_NAME")}"'
        cursor = db.cursor(buffered=True)
        cursor.execute(query)
        db.commit()
        db.close()
        return cursor.fetchall()

    @staticmethod
    def select_printer(estacion):
        """
        Function to get printer from station id
        """
        db = mysql.connector.connect(**b10_config)
        query = f'SELECT impre FROM station_conf WHERE no_estacion = "{estacion}"'
        cursor = db.cursor(buffered=True)
        cursor.execute(query)
        db.commit()
        db.close()
        return cursor.fetchall()

    @staticmethod
    def select_alt_printer(estacion):
        """
        Function to get printer from station id
        """
        db = mysql.connector.connect(**b10_config)
        query = f'SELECT impre_alt FROM station_conf WHERE no_estacion = "{estacion}"'
        cursor = db.cursor(buffered=True)
        cursor.execute(query)
        db.commit()
        db.close()
        return cursor.fetchall()

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
                    print(e)

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
            pass


    @staticmethod
    def select_printer_ext(linea):
        """
        Function to get printer from station id
        """
        db = mysql.connector.connect(**b10_config)
        query = f'SELECT impre FROM station_conf WHERE no_estacion = "{linea}"'
        cursor = db.cursor(buffered=True)
        cursor.execute(query)
        db.commit()
        db.close()
        return cursor.fetchall()