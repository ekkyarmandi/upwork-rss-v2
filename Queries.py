import json

class Queries:

    location = json.load(open("json/countries.json"))
    location = ",".join(location)
    param = dict(
        q="",
        title=None,
        ontology_skill_uid=None,
        subcategory2_uid=None,
        location=location
    )

    def __init__(self, payload, **params):
        self.payload = payload
        for key, value in params.items():
            self.param.update({key: value})
        self.payload.update(self.param)

    def construct(self):
        ''' Parse url parameter and return url'''
        params = []
        ref = "https://www.upwork.com/ab/feed/jobs/rss"
        for key,value in self.payload.items():
            params.append(str(key)+"="+str(value))
        url = ref+"?"+"&".join(params)
        url = url.replace(",","%2C").replace(" ","+")
        return url