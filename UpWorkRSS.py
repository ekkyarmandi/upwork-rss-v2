# import libraries
from tqdm import tqdm
import feedparser
import json

# import local functions and libraries
from JobPost import JobPost
from Queries import Queries
import query


class UpWorkRSS:

    categories_skills = json.load(open("json/categories-and-skills.json"))
    categories = categories_skills['Categories']
    skills = categories_skills['Skills']
    initial = True
    queries = []
    count = 0

    def __init__(self, profile_path):
        self.profile = json.load(open(profile_path))
        self.digest()

    def get(self):
        ''' Query result based on profile input '''

        if self.initial:
            pbar = tqdm(desc="Parser RSS Url",total=len(self.queries),unit="q")

        for url in self.queries:
            results = feedparser.parse(url)
            for entry in results['entries']:
                job = JobPost(entry)
                query.insert(
                    database="database/job_posts.db",
                    entry=job.to_dict()
                )
                self.count += 1
            
            try: pbar.update(1)
            except: pass
        try: pbar.close()
        except: pass

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