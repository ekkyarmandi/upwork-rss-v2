# Todo
# 1. Write folders creator function
# 2. Write database creator function

import sqlite3
import os

def check_folders(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_table(database="jobs.db", table="job"):
    con = sqlite3.connect(database)
    cur = con.cursor()
    cmd = f"""
    CREATE TABLE {table} (
        hash TEXT UNIQUE,
        title TEXT,
        description TEXT,
        link TEXT,
        budget TEXT,
        posted_on INTEGER,
        category TEXT,
        skills TEXT,
        country TEXT,
        live INTEGER
    )
    """
    cur.execute(cmd)
    con.commit()
    con.close()
    database = database.split("\\")[-1]
    print(f"{table} table has been created in {database}")

def update_table():
    pass

def delete_entries():
    pass