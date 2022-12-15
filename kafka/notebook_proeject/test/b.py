from stringprep import map_table_b2
from kafka import KafkaConsumer, KafkaProducer
import requests
from bs4 import BeautifulSoup as bs
import re
import time
import json


class Ine(object):
    
    def __init__(self):
        self.TOPIC_NAME="test"
        #self.brokers=["localhost:9091","localhost:9092","localhost:9093"]
        #self.producer = KafkaProducer(bootstrap_servers=self.brokers)
        self.URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
        self.target=["에르메스","루이비통","디올","프라다","구찌"]
        self.excepts=["삽니다","매입","구매","구입"]
    

    
    def get_item(self):
                
        #URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
        #my_arr=[]
        #is_first=True
        #target=["에르메스","루이비통","디올","프라다","구찌"]
        #excepts=["삽니다","매입","구매","구입"]

        html=requests.get(self.URL)
        soup_=html.text
        par_soup=bs(soup_, 'html.parser')
        tr_arr=par_soup.select("#main-area > div:nth-child(4) > table > tbody > tr")  
        return tr_arr
    
    def make_arr(self):
        my_arr=[]
        
        tr_arr=self.get_item()
        
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

                return my_arr

    def brand_name(self):
        #vo=Ine()
        get_item_=self.get_item()
        for element in get_item_:
            if not element["is_checked"]:
                element["is_checked"] = True

                if any(x in element["title"] for x in self.target) and not any(x in element["title"] for x in self.excepts):
                    clean_msg=vo.clean_text(element["title"])  
                    for m in clean_msg:
                        msg_split=clean_msg.split(" ")
                        for ms in msg_split:
                            if ms in self.target:
                                return ms
                                #print(ms)

    def clean_text(self,text):
        cleaned_text = re.sub('[a-zA-Z]','',text)
        cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned_text)

        return cleaned_text
            
#vo=Ine().producer
TOPIC_NAME="test"

vo=Ine()
#map=Ine.get_item()
map=vo.brand_name()
brokers=["localhost:9091","localhost:9092","localhost:9093"]
producer = KafkaProducer(bootstrap_servers=brokers)

producer.send(TOPIC_NAME, json.dumps(map).encode("utf-8"))
producer.flush()
time.sleep(1)


        
        
#ine=Vo_ine()
#ine.brand_name()

#vo=Vo_ine()
#print(vo.get_item())

# ine=Ine()
# ine.get_item()
    
# producer.send(ine.TOPIC_NAME, json.dumps(map).encode("utf-8"))
# producer.flush()        