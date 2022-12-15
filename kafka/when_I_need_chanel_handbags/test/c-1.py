from kafka import KafkaProducer

from bs4 import BeautifulSoup as bs
import re
from time import sleep
import redis 

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json


rd=redis.StrictRedis(host='127.0.0.1',port=6379,db=2)
url="http://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=334&search.boardtype=L"
my_arr=[]
recentSubject=""
is_first=True
target=["삼성","엘지","레노버","델","한성","애플"]
excepts=["삽니다","매입","구매","구입"]
TOPIC_NAME="test"

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.207 Whale/3.17.145.18 Safari/537.36'}

def requests_retry_session(retries=3,
                           backoff_factor=0.3,
                           status_forcelist=(500,502,504),
                           session=None):
    session=session or requests.Session()
    retry=Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter=HTTPAdapter(max_retries=retry)
    session.mount("http://",adapter)
    session.mount("http://",adapter)
    return session

def get_table_number(target_page):
    #with requests.Session() as s:
    res=requests_retry_session().get(target_page,timeout=10,headers=headers)
    if res.status_code==requests.codes.ok:
        par_soup=bs(res.text, 'html.parser')
        number=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr:nth-child(1) > td.td_article > div.board-number > div").text
        return number
    else:
        print("HTTP GET error!!")

def clean_text(text):
    cleaned_text = re.sub('[a-zA-Z]','',text)
    cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned_text)
    return cleaned_text

def brand_sorting(text):
    target_brand=''
    if '매입' in text:
        target_brand='업자'
    elif '애플' in text or "맥" in text or 'mac' in text:
        target_brand='애플'
    elif '삼성' in text:
        target_brand='삼성'
    elif '엘지' in text or 'LG' in text:
        target_brand='엘지'
    elif '아수스' in text or "에이수스" in text or "ASUS" in text or "asus" in text:
        target_brand='아수스'
    
    elif 'dell' in text or '델' in text or "DELL" in text:
        target_brand='DELL'
    elif '한성' in text:
        target_brand='한성'
    elif 'HP' in text or 'hp' in text:
        target_brand='HP'
    elif '레노버' in text or 'lenovo' in text or 'thinkpad' in text:
        target_brand='레노버'
    else:
        target_brand='기타 브랜드'
    return target_brand  

def map_the_dict():
    #with requests_retry_session.Session() as s:
    res=requests_retry_session().get(url,timeout=10,headers=headers)
    if res.status_code==requests.codes.ok:
        par_soup=bs(res.text, 'html.parser')
        tr_arr=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr")
        a_tag=tr_arr.select_one('td.td_article > div.board-list > div > a')
        map = {
        "title":a_tag.text.strip(),
        "url":'https://cafe.naver.com' + a_tag["href"],
        "brand": brand_sorting(a_tag.text.strip())
        }
        return map
    else:
        print("mapping request error!!!")

def kafka_connect(TOPIC_NAME,data):
    brokers=["localhost:9091","localhost:9092","localhost:9093"]
    producer = KafkaProducer(bootstrap_servers=brokers)
    producer.send(TOPIC_NAME, json.dumps(data).encode("utf-8"))
    producer.flush()

while True:
    number=get_table_number(url)
    if rd.sismember('done',number)==1:
        print('no new items')
        sleep(30)
    elif rd.sismember('done',number)==0:
        rd.delete('done')
        rd.sadd('done',number)
        print('start producing')
        print(map_the_dict())
        
        kafka_connect(TOPIC_NAME,map_the_dict())
        sleep(15)
    # if recentSubject==number:
    #     print('there is no new product')
    #     sleep(10)
    # elif recentSubject !=number:
    #     rd.sadd('done',recentSubject)
    #     recentSubject=number
        
    #     print(recentSubject,"new number -> start preprocessing")
    #     sleep(2)
    #     print(map_the_dict())
        
        # if any(x in map["title"] for x in target) and not any(x in map["title"] for x in excepts):
        #     msg_split=clean_text(map["title"]).split(" ")
        #     for msg in msg_split:
        #         for tar in target:
        #             val = msg.find(tar)
        #             if val !=-1:
        #                 map['brand']=tar
        #                 print("intermediate_stage.py로 데이터 전송, index:", val)
        #                 print(map)
        #                 sleep(3)
        
        
        # tr_arr=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr")
        # a_tag=tr_arr.select_one('td.td_article > div.board-list > div > a')
        # map = {
        # "title":a_tag.text.strip(),
        # "url":'https://cafe.naver.com' + a_tag["href"],
        # "brand": brand(a_tag.text.strip())
        # }
        # print(map)
        #         #sleep(2)
            # if any(x in map["title"] for x in target) and not any(x in map["title"] for x in self.excepts):
            #     msg_split=clean_text(map["title"]).split(" ")
            #     for msg in msg_split:
            #         for tar in target:
            #             val = msg.find(tar)
            #             if val !=-1:
            #                 map['brand']=tar
            #                 print("intermediate_stage.py로 데이터 전송, index:", val)
            #                 print(map)
#                                sleep(3)
        
    # for tr in tr_arr:
    #     is_new_item=True
    #     a_tag=tr.select_one('td.td_article > div.board-list > div > a')
    #     map = {
    #         "title":a_tag.text.strip(),
    #         "url":'https://cafe.naver.com' + a_tag["href"],
    #         "is_checked": False,
    #     }
    #     for element in my_arr:

    #         if element["url"] == map["url"]:
    #             is_new_item=False
    #             break
    #     if is_new_item:
    #         my_arr.insert(0,map)
            
            #print(map)
##############################################################################################################    
        # if not map["is_checked"]:
        #     map["is_checked"] = True

        #     if any(x in map["title"] for x in target) and not any(x in map["title"] for x in excepts):
        #         clean_msg=clean_text(map["title"])  
        #         for m in clean_msg:
        #             msg_split=clean_msg.split(" ")
        #         for ms in msg_split:
        #             if ms in target:
        #                 map['brand']=ms
        #             #else:
        #                 #map['brand']='None'
        #                 #print(map)
        #     else:
        #         map['brand']=None
                
        #         brokers=["localhost:9091","localhost:9092","localhost:9093"]
        #         producer = KafkaProducer(bootstrap_servers=brokers)

        #         producer.send(TOPIC_NAME, json.dumps(map).encode("utf-8"))
        #         producer.flush()
        #         sleep(1)
        #         print(map)
            
#{'title': '프라다 테수토 호보백 (22년3월구매 최신상)',
# 'url': 'https://cafe.naver.com/ArticleRead.nhn?clubid=10050146&page=1&menuid=782&boardtype=L&articleid=943911030&referrerAllArticles=false',
# 'is_checked': True}