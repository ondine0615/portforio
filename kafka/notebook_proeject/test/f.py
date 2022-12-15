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

                return map





vo=Ine()

print(vo.make_arr)