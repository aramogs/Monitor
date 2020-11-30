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

almacen_config = {
    'user': f'{os.getenv("DB_USER")}',
    'password': f'{os.getenv("DB_PASSWORD")}',
    'host': f'{os.getenv("DB_HOST")}',
    'database': f'{os.getenv("DB_PT_NAME")}',
    'raise_on_warnings': True
}


class DB:
    @staticmethod
    def get_printer(station):
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
        try:
            db = mysql.connector.connect(**almacen_config)
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
        try:
            db = mysql.connector.connect(**almacen_config)
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
    def select_tables():
            db = mysql.connector.connect(**b10_bartender_config)
            query = f'SELECT table_name FROM information_schema.tables WHERE table_schema = "{os.getenv("DB_BARTENDER_NAME")}"'
            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            db.commit()
            db.close()
            return cursor.fetchall()

    @staticmethod
    def select_printer(estacion):
        db = mysql.connector.connect(**b10_config)
        query = f'SELECT impre FROM station_conf WHERE no_estacion = "{estacion}"'
        cursor = db.cursor(buffered=True)
        cursor.execute(query)
        db.commit()
        db.close()
        return cursor.fetchall()

    @staticmethod
    def search_union(no_sap):
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

                db = mysql.connector.connect(**b10_bartender_config)
                query = f'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS ' \
                        f'WHERE TABLE_SCHEMA="{os.getenv("DB_BARTENDER_NAME")}" AND TABLE_NAME="{table[0]}";'
                cursor2 = db.cursor(buffered=True)
                cursor2.execute(query)
                db.commit()
                db.close()
                columns = cursor2.fetchall()
                # print("Columnas", columns)
                # print("Valores", values)
                return columns, values[0]



