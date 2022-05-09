# import libraries
from tqdm import tqdm
import feedparser
import json
import os

# import local functions and libraries
from JobPost import JobPost
from Queries import Queries
import query

# import rich libraries
from rich.console import Console
console = Console()


class UpWorkRSS:

    categories_skills = json.load(open("json/categories-and-skills.json"))
    categories = categories_skills['Categories']
    skills = categories_skills['Skills']
    queries = []
    count = 0

    def __init__(self, profile_path):
        self.profile = json.load(open(profile_path))
        self.digest()

    def get(self):
        ''' Query result based on profile input '''

        with console.status("[bright_green]Parser the RSS[/]") as status:
            for i,url in enumerate(self.queries):
                
                # updating the waiting text
                perc = 100*(i+1)/len(self.queries)
                status.update(f"[bright_green]Parser the RSS ({perc:.2f}%)[/]")

                # continue parse the rss url
                results = feedparser.parse(url)
                for entry in results['entries']:
                    job = JobPost(entry)
                    query.insert(
                        database="database/job_posts.db",
                        entry=job.to_dict()
                    )
                    self.count += 1

    def digest(self):
        ''' Digest rss.txt and turn it into variable before use it as url parameter'''

        with open("rss.txt",encoding='utf-8') as f:
            params = f.read().split("?")[1].split("&")
            params = {v.split("=")[0]:v.split("=")[1] for v in params}

        for key in self.profile:
            if key == "queries":
                for v in self.profile[key]:
                    query = Queries(
                        payload=params,
                        q=v
                    )
                    self.queries.append(query.construct())
            elif key == "title":
                for v in self.profile[key]:
                    query = Queries(
                        payload=params,
                        title=v
                    )
                    self.queries.append(query.construct())
            elif key == "skills":
                for v in self.profile[key]:
                    skill = self.skills[v]
                    query = Queries(
                        payload=params,
                        ontology_skill_uid=skill
                    )
                    self.queries.append(query.construct())
            elif key == "categories":
                categories = []
                for v in self.profile[key]:
                    category = self.categories[v]
                    categories.append(str(category))
                query = Queries(
                    payload=params,
                    subcategory2_uid=",".join(categories)
                )
                self.queries.append(query.construct())


if __name__ == "__main__":

    # collecting job post based on rss custom profile
    rss = UpWorkRSS("profile/scraping.json")
    rss.get()

    print("Total results:", rss.count, "jobs")