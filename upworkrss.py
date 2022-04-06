from pprint import pprint
from rss import RSS

import json

# Todo
# 1. Read User RSS, User Query (including adding skills and hastags)
# 2. Retrive all data using feedparser
# 3. Pushed all data into database
# 4. Pull and filter specfic information
# 5. Printout the job post on the terminal

class UpWorkRSS:

    def __init__(self, rss):
        self.rss_queries = []
        self.categories_skills = json.load(open("json/categories-and-skills.json"))
        self.rss_url_breakdown(rss)

    def rss_url_breakdown(self, rss):
        self.ref = rss.split("?")[0]
        self.param = {}
        for i in rss.split("?")[-1].split("&"):
            key = i.split("=")[0]
            value = i.split("=")[1]
            self.param.update({key:value})

    def read_profile(self, path):
        profile = json.load(open(path))
        queries = []
        for key in profile:
            if key == "queries":
                for q in profile[key]:
                    query = self.update_query(q=q)
                    queries.append(query)
            elif key == "title":
                for t in profile[key]:
                    query = self.update_query(title=t)
                    queries.append(query)
            elif key == "skills":
                for s in profile[key]:
                    query = self.update_query(ontology_skill_uid=str(self.categories_skills['Skills'][s]))
                    queries.append(query)
            elif key == "categories":
                categories = []
                for c in profile[key]:
                    categories.append(str(self.categories_skills['Categories'][c]))
                query = self.update_query(subcategory2_uid=",".join(categories))
                queries.append(query)
        json.dump(queries,open("queries.json","w"),indent=4)

    def update_query(self, **kwargs):
        query_param = self.param
        location = ",".join(json.load(open("json/countries.json")))
        param = {
            "q": "",
            "title": None,
            "ontology_skill_uid": None,
            "subcategory2_uid": None,
            "location": location
        }
        for k,v in kwargs.items():
            param[k] = v
        query_param.update(param)
        return query_param

if __name__ == "__main__":

    model = UpWorkRSS(RSS)
    model.read_profile("profile/scraping-and-nfts.json")