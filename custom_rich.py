from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from datetime import datetime

def rich_text(entry):
    
    # define the text format
    title = f"[white bold on magenta link={entry.link}]{entry.title.upper()}[/]"
    link = Text(entry.link, style="bright_blue")
    description = Panel(Text(entry.description, justify="left"), box=box.HORIZONTALS)
    tags = entry.tags
    location = Text(f"📍 {entry.country}", style="cyan", justify="right")

    # custom the budget text output
    if "N/A" not in entry.budget:
        budget = f"🤑 [bright_green bold blink]{entry.budget}[/]"
    else:
        budget = f"🤔 [yellow bold]{entry.budget}[/]"

    # custom the timestamp text output
    if entry.difftime() <= 3:
        timestamp = Text("\nPosted on: "+entry.calculate_time(), justify="right")
    else:
        timestamp = datetime.fromtimestamp(entry.timestamp)
        timestamp = Text("\nPosted on: "+timestamp.strftime("%d %b %Y"), justify="right")

    # create a grid table
    grid = Table.grid("")
    grid.add_row(title)
    grid.add_row(link)
    grid.add_row(description)
    grid.add_row(Align.center(tags))
    grid.add_row(timestamp)
    grid.add_row(location)

    # create main panel
    main_panel = Panel(
        grid,
        title=entry.category+" - "+ entry.hash,
        subtitle=budget,
        title_align="right",
        border_style="bright_green",
        width=120
    )

    # return rich renderable object
    return main_panel

if __name__ == "__main__":

    # import libraries
    import sqlite3
    import random

    # create a rich text output
    from rich import print
    from custom_rich import rich_text

    # import local library
    from Entry import Entry

    # query one row randomly
    con = sqlite3.connect("database/job_posts.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM jobs;")
    result = random.choice(cur.fetchall())
    entry = Entry(result)
    con.close()

    # print out the rich text
    main_panel = rich_text(entry)
    print(main_panel)