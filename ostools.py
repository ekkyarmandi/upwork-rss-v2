import sqlite3
import json
import re
import os

from datetime import datetime
import time

import colorama
from colorama import Fore, Back, Style
colorama.init()

def check_folders(path):
    '''
    Check folder/path existence
    '''
    if not os.path.exists(path):
        os.makedirs(path)

def create_table(database="jobs.db", table="job"):
    '''
    Create a new table
    '''
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
    '''
    Insert data into database
    '''
    def remove_none(dict):
        '''
        Change None value into null string
        '''
        for k,v in dict.items():
            if v == None:
                dict[k] = "null"
        return dict
    blacklist = json.load(open("json/blacklist-category.json"))
    con = sqlite3.connect("database/jobs.db")
    cur = con.cursor()
    if dict['category'] not in blacklist:
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
        cur.execute("UPDATE jobs SET budget = NULL WHERE budget = 'null'")
        cur.execute("UPDATE jobs SET skills = NULL WHERE skills = 'null'")
        con.commit()
    con.close()

def query_all(database,table,time_constrain,time_unit):

    # get time devider
    time_devider = {
        "hour": 3600,
        "minute": 60,
        "second": 1,
    }
    divider = time_devider[time_unit]
    
    # data query
    blacklist = json.load(open("json/blacklist-category.json"))
    now = datetime.now()
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute(f"SELECT posted_on,hash,category,live FROM {table} ORDER BY posted_on")
    data = cur.fetchall()
    results = []
    for j in data:
        job = {
            "timestamp": j[0],
            "hash": j[1],
            "category": j[2],
            "live": j[3]
        }
        difftime = int((now.timestamp()-job['timestamp'])/divider)
        if difftime <= time_constrain and job['category'] not in blacklist and job['live'] == 0:
            cur.execute(f"UPDATE {table} SET live = 1 WHERE hash=?",(job['hash'],))
            cur.execute(f"SELECT * FROM {table} WHERE hash=?",(job['hash'],))
            result = cur.fetchall()
            results.extend(result)
        elif difftime > time_constrain:
            cur.execute(f"DELETE FROM {table} WHERE hash=?",(job['hash'],))
    con.commit()
    con.close()
    return results

def unlive_all(database,table):
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute(f"UPDATE {table} SET live = 0")
    con.commit()
    con.close()

def print_entries(time_constrain, time_unit):
    '''
    Print all entries
    :param time_constrain: int -> Time constrain for filtering the jobs
    :param time_unit: str -> Time unit for time constrain
    '''

    # query and filter jobs
    jobs = query_all(
        database="database/jobs.db",
        table="jobs",
        time_constrain=time_constrain,
        time_unit=time_unit
    )

    # printout all jobs
    for job in jobs:
        result = {
            "title": job[1],
            "description": job[2],
            "link": job[3],
            "budget": job[4],
            "timestamp": datetime.fromtimestamp(job[5]),
            "category": job[6],
            "skills": job[7],
            "country": job[8]
        }
        result['description'] = re.sub("\s+"," ",result['description']).strip()
        if len(result['description']) > 360:
            result['description'] = result['description'][:360].strip(".").strip() + "..."
        if result['budget'] == None:
            result['budget'] = "Budget Unknown"
        print(f"{Fore.BLACK + Back.WHITE + result['title'] + Style.RESET_ALL} | {Fore.BLUE + result['category'] + Style.RESET_ALL} | {Fore.GREEN + result['budget'] + Style.RESET_ALL} ({result['timestamp'].strftime('%d/%m/%Y %H:%M:%S')})")
        print(f"{Fore.YELLOW + result['description'] + Style.RESET_ALL}")
        print(f"Link: {Fore.CYAN + result['link'] + Style.RESET_ALL}")
        print(f"Skills: {result['skills']}")
        print(f"Country: {Fore.CYAN + Back.MAGENTA + result['country'] + Style.RESET_ALL}")
        print()