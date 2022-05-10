from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from datetime import datetime
import time

class Entry:

    def __init__(self, entry):

        # assign the entry into self variable
        self.hash=entry[0]
        self.title=entry[1]
        self.description=entry[2]
        self.link=entry[3]
        self.budget=entry[4]
        self.timestamp=entry[5]
        self.category=entry[6]
        self.tags=" ".join(["[white on blue]#"+tag.replace(" ","")+"[/]" for tag in entry[7].split(",")])
        self.country=entry[8]

        # refine description text
        if len(self.description) > 360:
            self.description = self.description[:360].strip() + "..."
        
        if len(self.title) > 100:
            self.title = self.title[:100].strip() + "..."

        # refine budget text
        if self.budget == "N/A":
            self.budget = "Budget: " + self.budget
        elif "-" in self.budget:
            self.budget = "Hourly Range: " + self.budget
        else:
            self.budget = "Fixed Price: " + self.budget

    def calculate_time(self) -> str:
        ''' Convert timestamp into string '''

        seconds = int(time.time()-self.timestamp)
        hours, seconds = divmod(seconds,3600)
        minutes, seconds = divmod(seconds,60)
        if hours == 0:
            return f"{minutes} minute(s) ago"
        else:
            return f"{hours} hour(s) and {minutes} minute(s) ago"

    def difftime(self) -> int:
        ''' Calculate time differentiation '''

        seconds = int(time.time()-self.timestamp)
        hour, _ = divmod(seconds,3600)
        return hour

    def to_rich(self) -> Panel:
        ''' Turn string it into rich renderable format '''
    
        # define the text format
        title = f"[bright_green bold link={self.link}]{self.title.upper()}[/]"
        description = Panel(Text(self.description, justify="left"))
        location = Text(f"📍 {self.country}", style="cyan", justify="right")
        link = f"[cyan]{self.link}[/]"
        tags = self.tags

        # custom the budget text output
        if "N/A" not in self.budget:
            budget = f"🤑 [bright_green bold blink]{self.budget}[/]"
        else:
            budget = f"🤔 [yellow bold]{self.budget}[/]"

        # custom the timestamp text output
        if self.difftime() <= 3:
            timestamp = Text("\nPosted on: "+self.calculate_time(), justify="right")
        else:
            timestamp = datetime.fromtimestamp(self.timestamp)
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
            title=self.category+" - "+self.hash,
            subtitle=budget,
            title_align="right",
            border_style="bright_green",
            width=120
        )

        # return rich renderable object
        return main_panel