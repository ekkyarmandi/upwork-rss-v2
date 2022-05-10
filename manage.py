# necessary libraries
import argparse
import time

# import local library
import query as sql_fun
from UpWorkRSS import UpWorkRSS
from rich import print

# import rich libraries

'''
commands: {create_database,query}
usage: python manage.py create_table [-p] --path <database_path> [-t] --table <table_name>
usage: python manage.py query [-p] --profile <profile_path>
'''

parser = argparse.ArgumentParser(description="UpWork RSS Tools")

parser.set_defaults(create_table=False)
parser.set_defaults(query=False)

subparser = parser.add_subparsers()

databases = subparser.add_parser(
    "create_table",    
    help="Create new table"
)

databases.add_argument(
    "create_table",
    action="store_true",
    help="Create new table"
)

databases.add_argument(
    "-p", "--path",
    default="database/job_posts.db",
    help="Destination path"
)

databases.add_argument(
    "-t", "--table",
    default="job",
    help="Desired table name"
)

query = subparser.add_parser(
    "query",    
    help="Query syntax"
)

query.add_argument(
    "query",    
    action="store_true",
    help="Query syntax"
)

query.add_argument(
    "-p", "--profile",
    help="Profile path"
)

args = parser.parse_args()

if args.create_table:

    # create the database
    sql_fun.create_table(
        database=args.output,
        table=args.table
    )

elif args.query:

    # initiate the object
    rss = UpWorkRSS(args.profile)
    sql_fun.clear("database/job_posts.db")

    # parse rss url
    while True:
        rss.get()

        # query and print all results
        results = sql_fun.all_entries(
            database="database/job_posts.db",
            time_constrain=2 #hours
        )

        for entry in results:
            print(entry.to_rich())
            print()

        # put delay for 1 min
        time.sleep(60*1)