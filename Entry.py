import time

class Entry:

    def __init__(self, entry):
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

    def calculate_time(self):
        seconds = int(time.time()-self.timestamp)
        hours, seconds = divmod(seconds,3600)
        minutes, seconds = divmod(seconds,60)
        if hours == 0:
            return f"{minutes} minute(s) ago"
        else:
            return f"{hours} hour(s) and {minutes} minute(s) ago"

    def difftime(self) -> int:
        seconds = int(time.time()-self.timestamp)
        hour, _ = divmod(seconds,3600)
        return hour

    def __str__(self):
        n = 109
        msg = [
            " | ".join([
                self.title,
                self.category,
                self.budget,
                self.calculate_time()
            ]),
            "-"*n,
            self.description,
            "-"*n,
            self.link,
            "-"*n,
            "Tags: " + self.tags,
            "Country: " + self.country,
            "\n"
        ]
        return "\n".join(msg)