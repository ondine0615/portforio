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

target=["에르메스","루이비통","디올","프라다","구찌","샤넬"]
excepts=["삽니다","매입","구매","구입"]
recentSubject=""
TOPIC_NAME="test"

my_arr=[]
while True:    
    with requests.Session() as s:
        BASE_URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
        res=s.get(BASE_URL)
        if res.status_code==requests.codes.ok:
            par_soup=bs(res.text, 'html.parser')
            number=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr:nth-child(1) > td.td_article > div.board-number > div").text
            #print(number)
            if recentSubject==number:
                print('there is no new product')
                sleep(40)
                continue
            elif recentSubject !=number:
                recentSubject=number
                print(recentSubject)
                tr_arr=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr")
                a_tag=tr_arr.select_one('td.td_article > div.board-list > div > a')
                map = {
                "title":a_tag.text.strip(),
                "url":'https://cafe.naver.com' + a_tag["href"],
                "brand": " "
                }
                #print(map)
                #sleep(2)
        if any(x in map["title"] for x in target) and not any(x in map["title"] for x in excepts):
            msg_split=clean_text(map["title"]).split(" ")
            for msg in msg_split:
                for tar in target:
                    val = msg.find(tar)
                    if val !=-1:
                        map['brand']=tar
                        print("pipe.py로 데이터 동기화, index:", val)
    
            brokers=["localhost:9092"]
            producer = KafkaProducer(bootstrap_servers=brokers)

            producer.send(TOPIC_NAME, json.dumps(map).encode("utf-8"))
            producer.flush()
            print(map)
            sleep(40)