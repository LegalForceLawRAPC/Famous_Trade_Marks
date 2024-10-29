from dotenv import load_dotenv, dotenv_values
import os
import urllib
import requests
load_dotenv()


class KnowledgeGraph:
    API_KEY = ""
    url = ""
    q = ""

    def __init__(self,query):
        self.API_KEY = os.getenv("KNOWLEDGE_GRAPH_API_KEY")
        self.q = query

    def __build_request(self):
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        params = {
            'query': self.q,
            'limit': 10,
            'indent': True,
            'key': self.API_KEY,
        }
        self.url = service_url + '?' + urllib.parse.urlencode(params)
    
    def run(self):
        self.__build_request()
        resp = requests.get(self.url)
        return resp.json()