import os

from dotenv import load_dotenv

load_dotenv()
import mysql.connector

b10_config = {
    'user': f'{os.getenv("DB_USER")}',
    'password': f'{os.getenv("DB_PASSWORD")}',
    'host': f'{os.getenv("DB_HOST")}',
    'database': f'{os.getenv("DB_CONFIG_NAME")}',
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
        db = mysql.connector.connect(**b10_config)
        query = f'SELECT impre FROM b10.station_conf WHERE no_estacion = "{station}"'
        cursor = db.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        db.close()
        return result[0][0]

    @staticmethod
    def insert_partial_transfer(emp_num, part_num, no_serie, linea, transfer_order):
        db = mysql.connector.connect(**almacen_config)
        query = f'INSERT INTO partial_transfer (emp_num, part_num, no_serie, linea, transfer_order) ' \
                f'VALUES ({emp_num}, "{part_num}", {no_serie}, "{linea}", {transfer_order})'

        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        db.close()
        return cursor.rowcount

    @staticmethod
    def insert_complete_transfer(emp_num, no_serie, result, area):
        db = mysql.connector.connect(**almacen_config)
        query = f'INSERT INTO complete_transfer (emp_num, no_serie, result, area) ' \
                f'VALUES ({emp_num}, {no_serie}, "{result}", "{area}")'
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        db.close()
        return cursor.rowcount