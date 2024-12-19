
#imports
import requests
from requests import get
import os.path
import xml.etree.ElementTree as ET
import json
import pytrec_eval

CORE = "test"
BASE_URL = "http://localhost:8983/solr/"+ CORE + "/select?q="
DOCID = "id"
FIELDS = "&fl=" + DOCID + ",score"
ROWS = "&rows=1000"
RUN_FILE = 'baseline-title-abstract-query.run'
TAG = 'solr-bm25'
TOPICFILE = 'data/topics/topics-rnd5.xml'

# check if local Solr installtion is online
print(requests.get(BASE_URL).status_code)


# download the TREC-COVID topic file (round 5) from the NIST archive and safe a local copy

if os.path.isfile(TOPICFILE) != True:
    topicsfile = requests.get('https://ir.nist.gov/covidSubmit/data/topics-rnd5.xml', allow_redirects=True)
    open('topics-rnd5.xml', 'wb').write(topicsfile.content)

# query the title_txt field with the query taken from the topic file for all 50 topics

with open(TOPICFILE, 'r') as f:
    topicsxml = f.read() 

with open(RUN_FILE, 'w') as f_out:
    root = ET.parse(TOPICFILE).getroot()    
    for topic in root.findall('topic'):    

        query = topic.find('query').text
        topicId = topic.attrib['number']        

        # We assume that there are two fields index: title_txt and abstract_txt - Your milage may vary... 
        q = "title:(" + query.replace(' ', '%20') + ") " + "abstract:(" + query.replace(' ', '%20') + ")" # Change fieldtypes here!!!
        
        url = ''.join([BASE_URL, q, FIELDS, ROWS])
        print(url)
        json = get(url).json()        
        
        rank = 1                
        
        for doc in json.get('response').get('docs'):
            docid = doc.get(DOCID)            
            score = doc.get('score')
            out_str = '\t'.join([topicId, 'Q0', str(docid), str(rank), str(score), TAG])
            f_out.write(out_str + '\n')
            rank += 1

