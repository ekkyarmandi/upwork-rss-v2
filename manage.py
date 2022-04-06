# necessary libraries
import argparse
import ostools
import json

# UpWorkRSS class
from upworkrss import UpWorkRSS
from rss import RSS

parser = argparse.ArgumentParser(description="UpWork RSS Tools")
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
print(args)

if args.create_database:

    # check if the output is correct
    db_path = args.output.split("/")
    db_path = "/".join(db_path[:-1])
    ostools.check_folders(db_path)

    # create the database
    ostools.create_table(database=args.output, table=args.table)

elif args.query:

    # call the query
    model = UpWorkRSS(RSS)
    model.read_profile(
        path=args.profile
    )

    # printout the results