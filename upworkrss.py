# import libraries
from tqdm import tqdm
from rss import RSS
import feedparser
import ostools
import hashlib
import time
import json
import re

# Todo
# 1. Read User RSS, User Query (including adding skills and categories) ✔
# 2. Retrive all data using feedparser ✔
# 3. Pushed all data into database ✔
# 4. Pull and filter specific information
# 5. Printout the job post on the terminal

class UpWorkRSS:

    def __init__(self, rss):
        self.rss_queries = []
        self.categories_skills = json.load(open("json/categories-and-skills.json"))
        self.rss_url_breakdown(rss)
        ostools.unlive_all(
            database="database/jobs.db",
            table="jobs"
        )

    def rss_url_breakdown(self, rss):
        '''
        Breakdown RSS URL
        :param rss: str, RSS URL
        '''
        self.ref = rss.split("?")[0]
        self.param = {}
        for i in rss.split("?")[-1].split("&"):
            key = i.split("=")[0]
            value = i.split("=")[1]
            self.param.update({key:value})

    def read_profile(self, path):
        '''
        Turn dictionary profile into query parameter
        :param path: str, json file with object inside
        '''
        def update_query(query_param,**kwargs):
            '''
            Query updater
            :param query_param: dict, copy of rss parameter
            :param **kwargs: dict, all value associated with parameter
            :return query_param: dict, the updated rss parameter
            '''

            # load the allowed country list
            location = ",".join(json.load(open("json/countries.json")))
            
            # prepare new parameter
            param = {
                "q": "",
                "title": None,
                "ontology_skill_uid": None,
                "subcategory2_uid": None,
                "location": location
            }

            # iterate keys and values from kwargs
            for k,v in kwargs.items(): param[k] = v
            
            # update query parameter
            query_param.update(param)
            return query_param

        # read profile
        profile = json.load(open(path))

        # iterate profile and read each key as seperate rss query parameter
        for key in profile:
            if key == "queries":
                for q in profile[key]:
                    self.rss_queries.append(update_query(self.param,q=q))
            elif key == "title":
                for t in profile[key]:
                    self.rss_queries.append(update_query(self.param,title=t))
            elif key == "skills":
                for s in profile[key]:
                    skill = str(self.categories_skills['Skills'][s])
                    self.rss_queries.append(update_query(self.param,ontology_skill_uid=skill))
            elif key == "categories":
                categories = []
                for c in profile[key]:
                    categories.append(str(self.categories_skills['Categories'][c]))
                self.rss_queries.append(update_query(self.param,subcategory2_uid=",".join(categories)))
    
    def gather(self,entry):
        '''
        Gather job entry.
        :param entry: dict -> job feed entry
        '''

        def replace(text):
            '''
            Replace some character into readable sign.
            :param/return text: str -> target text
            '''
            signs = json.load(open("./json/signs.json"))
            while any([True if s in text else False for s in signs]):
                for key,value in signs.items():
                    text = text.replace(key,value)
            return text
        
        # find job title and hashing it
        job_title = entry['title'].replace("- Upwork","").strip()
        encoded_str = bytes(job_title,'utf-8')

        # assign initial value
        job = {
            "hash": hashlib.md5(encoded_str).hexdigest(),
            "title": replace(job_title),
            "link": entry['link'].strip("?source=rss"),
            "budget": None,
            "skills": None
        }
        
        # find text with bold
        rm = []
        details = replace(entry['content'][0]['value'])
        for b in re.finditer("(?<=\<b\>)(.*?)(?=\<\/b\>)",details):
            rm.append(b.start())
            title = details[b.start():b.end()]
            if "Posted On" not in title:
                text = details[b.start():]
                x = re.search("\<br \/\>",text)
                text = text[:x.end()].replace("<br />","")
                text = text.replace(f"{title}</b>:","").strip()
                if title == "Skills":
                    title = title.lower().replace(" ","_")
                    text = ", ".join(["#"+s.strip() for s in text.split(",")])
                    job.update({title:text})
                elif "Budget" in title or "Hourly" in title:
                    title = title.lower().replace(" ","_")
                    job.update({"budget":text})
                else:
                    title = title.lower().replace(" ","_")
                    job.update({title:text})

        # clean the description
        new_details = details[:min(rm)].replace("<b>","")
        new_details = new_details.replace("<br />","\n")
        new_details = re.sub("\n+","\n",new_details).strip()        
        job.update({"description": new_details})

        # modifying posted on date value
        job.update({"posted_on": int(time.mktime(entry['published_parsed']))+(7*3600)}) # Convert UTC -> GMT+7

        # insert job into database
        ostools.insert(job)
    
    def parse_all(self):
        '''
        Parser all saved rss queries
        '''

        # iterate gatherd queries
        bar_format = "querying rss url {percentage:3.2f}% ({elapsed_s:.2f} sec)"
        for param in tqdm(self.rss_queries, bar_format=bar_format):
            
            # turn dictionary into url
            params = [str(k) + "=" + str(v) for k,v in param.items() if v != None]
            url = self.ref + "?" + "&".join(params)
            url = url.replace(",","%2C").replace(" ","+")
            
            # parser url
            results = feedparser.parse(url)

            # insert all retrieved entries into database
            for entry in results['entries']:
                self.gather(entry)

if __name__ == "__main__":

    model = UpWorkRSS(RSS)
    model.read_profile("profile/scraping.json")
    model.parse_all()

    ostools.print_entries(time_constrain=2,time_unit="hour")