# necessary libraries
import argparse
import time

# import local library
from UpWorkRSS import UpWorkRSS
from custom_rich import rich_text
from rich import print
import query as sql_fun

# import rich libraries

'''
commands: {create_database,query}
usage: python manage.py create_database --output <database_path> --table <table_name>
usage: python manage.py query --profile <profile_path>
'''

parser = argparse.ArgumentParser(description="UpWork RSS Tools")

parser.set_defaults(create_database=False)
parser.set_defaults(query=False)

subparser = parser.add_subparsers()

databases = subparser.add_parser(
    "create_database",    
    help="Create new database"
)

databases.add_argument(
    "create_database",
    action="store_true",
    help="Create new database"
)

databases.add_argument(
    "-o", "--output",
    default="database/jobs.db",
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

if args.create_database:

    # create the database
    sql_fun.create_table(
        database=args.output,
        table=args.table
    )

elif args.query:

    # initiate the object
    rss = UpWorkRSS(args.profile)
    sql_fun.reset_printed(database="database/job_posts.db")

    # parse rss url
    while True:
        rss.get()

        # query and print all results
        results = sql_fun.all_entries(
            database="database/job_posts.db",
            time_constrain=2
        )

        for post in results:
            entry = rich_text(post)
            print(entry)
            print()

        # put delay for 1 min
        time.sleep(60*1)