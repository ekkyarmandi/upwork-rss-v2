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
        post_date = datetime.fromttimestamp(job['timestamp'])
        post_date = post_date.strftime("%H:%M:%S %d %b %Y")
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

    # query and filter jobs
    jobs = query_all(
        database="database/jobs.db",
        table="jobs",
        time_constrain=time_constrain,
        time_unit=time_unit
    )

    # printout all jobs
    for job in jobs:
        pass

def sec2hms(sec):
    '''
    Converting seconds to Hours and Minute
    :param sec: int -> seconds
    :return timestr: str -> formatted seconds
    '''
    m, _ = divmod(sec, 60)
    if m <= 60:
        if m == 1: return f"{int(m):d} minute ago"
        else: return f"{int(m):d} minutes ago"
    elif m > 60:
        h, m = divmod(m, 60)
        if m == 1: return f"{int(h):d} hours and {int(m):d} minute ago"
        else: return f"{int(h):d} hours and {int(m):d} minutes ago"

def print_output(results,initial=False):
    '''
    Printout the retrived jobs.
    :param results: list -> List of jobs
    '''
    now = time.time()
    for i in range(len(results)):
        result = results[i]
        output = {
            "title": result[1],
            "description": result[2],
            "link": result[3],
            "budget": result[4],
            "timestamp": sec2hms(now-result[5]),
            "category": result[6],
            "skills": result[7],
            "country": result[8]
        }
        output['description'] = re.sub("\s+"," ",output['description']).strip()
        if len(output['description']) > 360:
            output['description'] = output['description'][:360].strip(".").strip() + "..."
        if output['budget'] == None:
            output['budget'] = "Budget Unknown"
        print(f"{Fore.BLACK + Back.WHITE + output['title'] + Style.RESET_ALL} | {Fore.BLUE + output['category'] + Style.RESET_ALL} | {Fore.GREEN + output['budget'] + Style.RESET_ALL} ({output['timestamp']})")
        print(f"{Fore.YELLOW + output['description'] + Style.RESET_ALL}")
        print(f"Link: {Fore.CYAN + output['link'] + Style.RESET_ALL}")
        print(f"Skills: {output['skills']}")
        print(f"Country: {Fore.CYAN + Back.MAGENTA + output['country'] + Style.RESET_ALL}")
        print()