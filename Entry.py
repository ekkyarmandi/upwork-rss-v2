import time

class Entry:

    def __init__(self, title, description, link, budget, timestamp, category, tags, country):
        self.title=title
        self.description=description
        self.link=link
        self.budget=budget
        self.timestamp=timestamp
        self.category=category
        self.tags=", ".join(["#"+tag for tag in tags.split(",")])
        self.country=country

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
        return f"{hours} hour(s) and {minutes} minute(s) ago"

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