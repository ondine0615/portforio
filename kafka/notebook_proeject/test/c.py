from kafka import KafkaProducer
import requests
from bs4 import BeautifulSoup as bs
import re
from time import sleep
import json

def clean_text(text):
        cleaned_text = re.sub('[a-zA-Z]','',text)
        cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned_text)
        return cleaned_text


URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
my_arr=[]
is_first=True
target=["에르메스","루이비통","디올","프라다","구찌","샤넬"]
excepts=["삽니다","매입","구매","구입"]

html=requests.get(URL)
soup=html.text
par_soup=bs(soup, 'html.parser')
tr_arr=par_soup.select("#main-area > div:nth-child(4) > table > tbody > tr")  
TOPIC_NAME="test"

while True:
        
    for tr in tr_arr:
        is_new_item=True
        a_tag=tr.select_one('td.td_article > div.board-list > div > a')
        map = {
            "title":a_tag.text.strip(),
            "url":'https://cafe.naver.com' + a_tag["href"],
            "is_checked": False,
        }
        for element in my_arr:

            if element["url"] == map["url"]:
                is_new_item=False
                break
        if is_new_item:
            my_arr.insert(0,map)
            
            #print(map)
##############################################################################################################    
        if not map["is_checked"]:
            map["is_checked"] = True

            if any(x in map["title"] for x in target) and not any(x in map["title"] for x in excepts):
                clean_msg=clean_text(map["title"])  
                for m in clean_msg:
                    msg_split=clean_msg.split(" ")
                for ms in msg_split:
                    if ms in target:
                        map['brand']=ms
                    #else:
                        #map['brand']='None'
                        #print(map)
            else:
                map['brand']=None
                
                brokers=["localhost:9091","localhost:9092","localhost:9093"]
                producer = KafkaProducer(bootstrap_servers=brokers)

                producer.send(TOPIC_NAME, json.dumps(map).encode("utf-8"))
                producer.flush()
                sleep(1)
                print(map)
            
#{'title': '프라다 테수토 호보백 (22년3월구매 최신상)',
# 'url': 'https://cafe.naver.com/ArticleRead.nhn?clubid=10050146&page=1&menuid=782&boardtype=L&articleid=943911030&referrerAllArticles=false',
# 'is_checked': True}