import sqlite3
import json
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

def insert(dict):
    def remove_none(dict):
        for k,v in dict.items():
            if v == None:
                dict[k] = "null"
        return dict
    blacklist = json.load(open("json/blacklist-category.json"))
    con = sqlite3.connect("database/jobs.db")
    cur = con.cursor()
    cur.execute(f"SELECT title FROM jobs WHERE hash = '{dict['hash']}'")
    existing = cur.fetchone()
    if dict['category'] not in blacklist and existing is None:
        dict = remove_none(dict)
        cmd = """INSERT or IGNORE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?)"""
        cur.execute(cmd, (
            dict['hash'],
            dict['title'],
            dict['description'],
            dict['link'],
            dict['budget'],
            dict['posted_on'],
            dict['category'],
            dict['skills'],
            dict['country'],
            0
        ))
        cur.execute("UPDATE jobs SET budget = NULL where budget = 'null'")
        cur.execute("UPDATE jobs SET skills = NULL where skills = 'null'")
        con.commit()
    con.close()

def delete_entries():
    pass