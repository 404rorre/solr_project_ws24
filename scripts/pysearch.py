
#imports
import requests
from requests import get
import os.path
import xml.etree.ElementTree as ET
import json
from tqdm import tqdm
import pandas as pd

class QUERY():
    """ 
    Queries solr with different cores and queries and topics.
    Returns a *.run file with results.
    """
    def __init__(self, version: str=None, 
                 core: str=None, 
                 rows: int=1000, 
                 url_query: str=None, 
                 df_topics: pd.DataFrame=None, 
                 topicfile: str='data/topics/topics-rnd5.xml'
                 ):
        """ 
        Init Parameters
        """
        # URL parameters
        self.core = core
        self.base_url = "http://localhost:8983/solr/"+ self.core + "/select?q="
        self.docid = "id"
        self.fields = "&fl=" + self.docid + ",score"
        self.rows = f"&rows={rows}"
        self.run_file = f"{core}_{version}.run"
        self.url_query = url_query
        self.version = f"{core}_{version}"
        self.df_topics = df_topics
        self.topicfile = topicfile
        self.f_new_topic = True if isinstance(df_topics, pd.DataFrame) else False
            
    def run(self):
        """ 
        Runs whole topic with respective solr core.
        """
        if self.url_live():
            self.check_topic()
            if self.url_query:
                self.run_queries()
            else:
                print("Aborted run: Query missing!")
        else:
            print("Aborted run.")
            print("Core does not exist, or solr is not started yet.")

    def url_live(self):
        """
        Checks if Solr is live and core exists.
        Returns bool.
        """
        live = get(self.base_url)
        print(self.base_url)
        if "200" in str(live):
            print(f"\nCore \"{self.core}\" is live: {live}")
            return True
        else:
            print(f"\nCore \"{self.core}\" has Status: {live}")
            return False    

    def check_topic(self):
        """
        Checks if topic xml file exists. If no Download new topic xml from source.
        """
        if os.path.isfile(self.topicfile) != True:
            print("\nTopic file not found downloading new from source...")
            topicsfile = requests.get('https://ir.nist.gov/covidSubmit/data/topics-rnd5.xml', allow_redirects=True)
            open(self.topicfile, 'wb').write(topicsfile.content)
        else:
            print("\nTopic file exists continue to next step...")
        
    def gen_query_url(self, url_query: str=None, idx_topic: int=None):
        """ 
        Returns arbitrary query.
        """
        # cleans white spaces
        url_query = url_query.replace(" ", "%20")
        # checks if topic parts are present in url and replaces it with value
        if self.query:
            url_query = url_query.replace("query",f"{self.query}")
        if self.question:
            url_query = url_query.replace("question",f"{self.question}")
        if self.narrative:
            url_query = url_query.replace("narrative",f"{self.narrative}")
        for col in range(len(self.df_topics.columns) -4+1): # reducing range in for loop by -4 because of the original columns of the topic file # +1 for including last column
            col = col+4 # expanding again for right column index # -1 for index counting (off by one)
            url_query = url_query.replace(f"${col}",f"{self.df_topics.iloc[idx_topic, col-1]}")
            
        return url_query

    def run_queries(self):
        """ 
        Runs whole topics.
        """
        # query the title_txt field with the query taken from the topic file for all 50 topics
        if not self.f_new_topic:
            print("Using manipulated Topics.")
            if ".csv" in self.topicfile:
                self.df_topics = pd.read_csv(self.topicfile)
            if ".xml" in self.topicfile:
                self.df_topics = pd.read_xml(self.topicfile)
        else:
            print("Using standard Topics. (no manipulation)")
        
        print(f"Start run: {self.run_file}\n")
        with open(self.run_file, 'w') as f_out:

            for idx_topic in range(len(self.df_topics)):    

                self.query = self.df_topics["query"][idx_topic]
                self.question= self.df_topics["question"][idx_topic]
                self.narrative= self.df_topics["narrative"][idx_topic]
                self.topicId = str(self.df_topics["number"][idx_topic])   

                # We assume that there are two fields index: title_txt and abstract_txt - Your milage may vary... 
                q = self.gen_query_url(url_query=self.url_query,idx_topic=idx_topic)
                print(q)
                
                url = ''.join([self.base_url, q, self.fields, self.rows])
                #print(url)
                json = get(url).json()        
                
                rank = 1                
                
                for doc in json.get('response').get('docs'):
                    docid = doc.get(self.docid)            
                    score = doc.get('score')
                    out_str = '\t'.join([self.topicId, 'Q0', str(docid), str(rank), str(score), self.version])
                    f_out.write(out_str + '\n')
                    rank += 1
        print(f"Finished run: {self.run_file}\n")
                    
if __name__=="__main__":
    query = "title:(query) abstract:(query)"
    solr = QUERY(version="test_v1", 
                 core="base_bm25", 
                 rows=1000, 
                 url_query=query)
    
    solr.run()

