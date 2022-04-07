# necessary libraries
import argparse
from venv import create
import ostools

# UpWorkRSS class
from upworkrss import UpWorkRSS
from rss import RSS

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

    # check if the output is correct
    db_path = args.output.split("/")
    db_path = "/".join(db_path[:-1])
    ostools.check_folders(db_path)

    # create the database
    ostools.create_table(
        database=args.output,
        table=args.table
    )

elif args.query:

    while True:

        # call the query
        model = UpWorkRSS(RSS)
        model.read_profile(
            path=args.profile
        )
        model.parse_all()

        # printout the results
        ostools.print_entries(
            time_constrain=2,
            time_unit="hour"
        )