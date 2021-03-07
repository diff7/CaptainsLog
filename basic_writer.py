import os
import re
from copy import copy
import sqlite3
from sqlite3 import Error
from datetime import datetime


def get_tags(s):
    pat = re.compile(r"#(\w+)")
    return " ".join(pat.findall(s))


def write(connecor, record, name):
    now = datetime.now()
    record = record.replace("'", "")
    tags = get_tags(record)
    unique_key = now.strftime("%Y-%m-%d %H:%M:%S") + " " + name
    db_record = {
        "unique_key": unique_key,
        "record": record,
        "tags": tags,
        "name": name,
    }
    connecor.add_record(db_record)


class SqlConnect:
    conn = None
    cursor = None

    def __init__(self, db_path, table_name="records", primary_key="name"):

        self.db_path = db_path
        self.table_name = table_name
        self.primary_key = primary_key
        self.key = "unique_key"

        if not os.path.isfile(self.db_path):
            print(f"Did not find database, creating a new one {self.db_path}")
        self.create_connection()

        table_exists = self.fetch_query(
            f"""SELECT name FROM sqlite_master
                                        WHERE type='table' AND name='{self.table_name}';"""
        )
        if len(table_exists) == 0:
            print(f"Creating table: {self.table_name}")
            self.create_main_table()

        self.default_table_dict = {
            self.key: "",
            "name": "",
            "record": "#",
            "tags": "#",
        }

    def create_connection(self):
        """ create a database connection to a SQLite database """
        # if SqlConnect.conn is None:
        try:
            SqlConnect.conn = sqlite3.connect(
                self.db_path, check_same_thread=False
            )
            SqlConnect.cursor = self.conn.cursor()
        except Error as e:
            print(e)

    def execute_sql(self, sql):
        try:
            c = SqlConnect.conn.cursor()
            c.execute(sql)
        except Error as e:
            print(e)
        SqlConnect.conn.commit()

    def fetch_query(self, sql):
        try:
            c = SqlConnect.conn.cursor()
            c.execute(sql)
        except Error as e:
            print(e)
        result = c.fetchall()
        return result

    def create_main_table(self):
        create_table_sql = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            {self.key} text PRIMARY KEY,
            name text NOT NULL,
            record text NOT NULL,
            tags text,
            time_utc DATETIME DEFAULT CURRENT_TIMESTAMP
            );"""

        print(create_table_sql)
        self.execute_sql(create_table_sql)

    def check_if_record_exists(self, key):
        sql_if_exists = f""" SELECT {self.primary_key} FROM {self.table_name} WHERE time = '{key}' """
        result = self.fetch_query(sql_if_exists)
        if len(result) > 0:
            return True
        else:
            return False

    def add_record(self, new_records_dict):
        # CREATE A MODEL RECORD
        new_values = copy(self.default_table_dict)
        new_values.update(new_records_dict)
        print(f"Creating a new record for {self.table_name}")
        columns = ",".join(new_values.keys())
        values = ",".join(["'" + str(v) + "'" for v in new_values.values()])
        sql_insert_model = (
            f""" Insert into {self.table_name}({columns}) values({values})"""
        )
        self.execute_sql(sql_insert_model)

    def update(self, new_records_dict, key_value):
        new_values = copy(self.default_table_dict)
        new_values.update(new_records_dict)

        print(f"Updating {self.table_name}")
        sql_update = "UPDATE {} SET ".format(self.table_name)
        items = ""
        for key in new_values:
            if key == "name":
                continue
            items += key + "= '" + str(new_values[key]) + "' ,"
        sql_update += "{}  WHERE name == '{}'".format(items[:-1], key_value)
        self.execute_sql(sql_update)

    def add_or_update(self, new_records_dict):
        key_value = new_records_dict[self.key]
        exists = self.check_if_record_exists(key_value)
        if exists:
            self.update(new_records_dict, key_value)
        else:
            self.add_record(new_records_dict)

    def update_one(self, model, column, value):
        sql_update = "UPDATE {} SET {} = '{}' WHERE name = '{}'".format(
            self.table_name, column, value
        )
        self.execute_sql(sql_update)

    def close(self):
        SqlConnect.conn.close()