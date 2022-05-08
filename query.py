# import sqlite libraries
import sqlite3
import json
from datetime import datetime

# import Objects
from Entry import Entry


def create_table(database: str, table: str) -> None:
    '''
    Create a new table
    :param database: str, database path
    :param table: str, table name
    '''
    
    # connect to database and create a table
    con = sqlite3.connect(database)
    cur = con.cursor()
    cmd = f"""
    CREATE TABLE {table} (
        hash TEXT UNIQUE,
        title TEXT,
        description TEXT,
        link TEXT,
        budget TEXT,
        timestamp INTEGER,
        category TEXT,
        tags TEXT,
        country TEXT,
        printed INTEGER
    )
    """
    cur.execute(cmd)
    con.commit()
    con.close()

def insert(database: str, entry: dict) -> None:
    '''
    Insert data into database
    :param database: str, database path
    :param entry: str, an entries
    '''
    def remove_none(dict):
        '''
        Change None value into null string
        :param dict: dict
        :return:
        '''
        for k,v in dict.items():
            if v == None:
                dict[k] = "null"
        return dict

    # load the blacklist data
    forbidden_category = json.load(open("json/blacklist-category.json"))
    forbidden_text = json.load(open("json/blacklist-description.json"))

    # connect to the database
    con = sqlite3.connect(database)
    cur = con.cursor()
    if entry['category'] not in forbidden_category and all([t not in entry['description'] for t in forbidden_text]):
        entry = remove_none(entry)
        cmd = """INSERT or IGNORE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?)"""
        cur.execute(cmd, (
            entry['hash'],
            entry['title'],
            entry['description'],
            entry['link'],
            entry['budget'],
            entry['timestamp'],
            entry['category'],
            entry['tags'],
            entry['country'],
            0
        ))
        cur.execute("UPDATE jobs SET budget = NULL WHERE budget = 'null'")
        cur.execute("UPDATE jobs SET tags = NULL WHERE tags = 'null'")
        con.commit()
    con.close()

def reset_printed(database: str, table: str = "jobs") -> None:
    '''
    Set printed column into false
    '''
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute(f"UPDATE {table} SET printed = 0")
    con.commit()
    con.close()

def all_entries(database: str, table: str = "jobs", time_constrain: int = 3) -> list:
    '''
    Query all entries
    :param database: str, database path
    :param table: str, table name
    :param time_constrain: int, the maximum hours for the latest job posted
    :return entries: list, queried results
    '''
    
    # connect to the database
    now = datetime.now()
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute(f"SELECT timestamp,hash,printed FROM {table} ORDER BY timestamp")
    data = cur.fetchall()
    
    # filter the query results
    results = []
    for j in data:
        
        # turn the query result into dictionary
        entry = {
            "posted_on": int((now.timestamp()-j[0])/3600),
            "hash": j[1],
            "printed": j[2]
        }
        
        # filter based on time constrain variable and it's not printed out yet
        if entry['posted_on'] <= time_constrain and entry['printed'] == 0:
            cur.execute(f"UPDATE {table} SET printed = 1 WHERE hash=?",(entry['hash'],))
            cur.execute(f"SELECT * FROM {table} WHERE hash=?",(entry['hash'],))
            result = cur.fetchone()
            post = Entry(
                title=result[1],
                description=result[2],
                link=result[3],
                budget=result[4],
                timestamp=result[5],
                category=result[6],
                tags=result[7],
                country=result[8]
            )
            results.append(post)
        
        # delete the post if the post is outdated
        elif entry['posted_on'] > time_constrain:
            cur.execute(f"DELETE FROM {table} WHERE hash=?",(entry['hash'],))

    # commit the changes and then close the database
    con.commit()
    con.close()

    # return the results
    return results

if __name__ == "__main__":

    # Test: Create a table
    # create_table("database/job_posts.db","jobs")

    # Test: Do jobs query from database
    database = "database/job_posts.db"
    reset_printed(database)
    results = all_entries(database)
    for post in results:
        print(post)