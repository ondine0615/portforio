import requests
from bs4 import BeautifulSoup as bs
import json
import time

from kafka import KafkaProducer
# Kafka Setting 


TOPIC_NAME="test"
brokers=["localhost:9091","localhost:9092","localhost:9093"]
producer = KafkaProducer(bootstrap_servers=brokers)
        
    

        
URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
my_arr=[]
is_first=True
target=["에르메스","루이비통","디올","프라다","구찌","샤넬"]
excepts=["삽니다","매입","구매","구입"]

html=requests.get(URL)
soup=html.text
par_soup=bs(soup, 'html.parser')
tr_arr=par_soup.select("#main-area > div:nth-child(4) > table > tbody > tr")  

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

    
        producer.send(TOPIC_NAME, json.dumps(map).encode("utf-8"))
        producer.flush()
        time.sleep(1)


# class Ine(object):
    
#     def __init__(self):
#         self.TOPIC_NAME="test"
#         self.brokers=["localhost:9091","localhost:9092","localhost:9093"]
#         self.producer = KafkaProducer(bootstrap_servers=self.brokers)
        
#     def get_item(self):
                
#         URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
#         my_arr=[]
#         is_first=True
#         target=["에르메스","루이비통","디올","프라다","구찌"]
#         excepts=["삽니다","매입","구매","구입"]

#         html=requests.get(URL)
#         soup=html.text
#         par_soup=bs(soup, 'html.parser')
#         tr_arr=par_soup.select("#main-area > div:nth-child(4) > table > tbody > tr")  

#         while True:
                
#             for tr in tr_arr:
#                 is_new_item=True
#                 a_tag=tr.select_one('td.td_article > div.board-list > div > a')
#                 map = {
#                     "title":a_tag.text.strip(),
#                     "url":'https://cafe.naver.com' + a_tag["href"],
#                     "is_checked": False,
#                 }
#                 for element in my_arr:
#                     if element["url"] == map["url"]:
#                         is_new_item=False
#                         break
#                 if is_new_item:
#                     my_arr.insert(0,map)

#             return my_arr

# ine=Ine()
# ine.get_item()
    
# producer.send(ine.TOPIC_NAME, json.dumps(map).encode("utf-8"))
# producer.flush()


        #return tr_arr
    
    

        #print(my_arr)
        