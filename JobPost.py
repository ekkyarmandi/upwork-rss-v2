from bs4 import BeautifulSoup
import hashlib
import query
import time
import re


def refine_text(text):
    text = text.lstrip(":")
    return text.strip()

class JobPost:

    title = ""
    link = ""
    description = "N/A"
    short_desc = "N/A"
    timestamp = ""
    category = ""
    country = ""
    budget = "N/A"
    tags = []

    def __init__(self, entry):

        # refine title and hashing it
        self.hashing(entry['title'])

        # refine the link
        self.link = entry['link']

        # collect job description, job category, origin country, budget, and skill tags
        text = entry['content'][0]['value']
        content = BeautifulSoup(text,"html.parser")
        self.find_description(text)
        self.find_country(content)
        self.find_category(content)
        self.collect_budget(content)
        self.collect_tags(content)

        # convert the timestamp
        self.timestamp = int(time.mktime(entry['published_parsed']))+(7*3600)

    def hashing(self, title):
        title = title.strip("Upwork").strip()
        self.title = " ".join(re.findall("[A-Za-z0-9]+",title))
        self.hash = hashlib.md5(bytes(self.title,"utf-8")).hexdigest()

    def find_description(self, text):
        b = re.search("<b>",text)
        if b != None:
            soup = BeautifulSoup(text[:b.start()],"html.parser")
            self.description = re.sub("\s+"," ",soup.text).strip()
            self.short_desc = self.description[:360].strip()+"..."

    def find_country(self,content):
        for b in content.find_all("b"):
            if b.text == "Country":
                self.country = refine_text(b.next_sibling)
                break

    def find_category(self,content):
        for b in content.find_all("b"):
            if b.text == "Category":
                self.category = refine_text(b.next_sibling)
                break

    def collect_budget(self, content):
        for b in content.find_all("b"):
            if b.text in ["Budget","Hourly Range"]:
                self.budget = refine_text(b.next_sibling) 
                break

    def collect_tags(self, content):
        for b in content.find_all("b"):
            if b.text == "Skills":
                self.tags = refine_text(b.next_sibling)
                self.tags = self.tags.split(",")
                self.tags = [tag.strip() for tag in self.tags]
                break

    def to_dict(self):
        return dict(
            hash=self.hash,
            title=self.title,
            link=self.link,
            description=self.description,
            timestamp=self.timestamp,
            category=self.category,
            country=self.country,
            budget=self.budget,
            tags=",".join(self.tags)
        )

    def insert(self):
        query.insert(
            database="database/job_posts.db",
            entry=self.to_dict()
        )

    def __str__(self):
        return self.title