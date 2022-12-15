from kafka import KafkaProducer
import requests
from bs4 import BeautifulSoup as bs
import re
from time import sleep

url="http://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=334&search.boardtype=L"
my_arr=[]
recentSubject=""
is_first=True
target=["에르메스","루이비통","디올","프라다","구찌","샤넬"]
excepts=["삽니다","매입","구매","구입"]
TOPIC_NAME="test"

def get_table_number(self,base_url):
    html=requests.get(base_url)
    soup=html.text
    par_soup=bs(soup, 'html.parser')
    #tr_arr=par_soup.select("#main-area > div:nth-child(4) > table > tbody > tr")
    number=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr:nth-child(1) > td.td_article > div.board-number > div").text
    return number
    

def clean_text(text):
    cleaned_text = re.sub('[a-zA-Z]','',text)
    cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned_text)
    return cleaned_text


while True:

    with requests.Session() as s:
        res=s.get(url)
        if res.status_code==requests.codes.ok:
            par_soup=bs(res.text, 'html.parser')
            number=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr:nth-child(1) > td.td_article > div.board-number > div").text
            
            
            if recentSubject==number:
                print('there is no new product')

                sleep(10)
                
            elif recentSubject !=number:
                recentSubject=number
                print(recentSubject,"new number -> start preprocessing")
                sleep(2)
                tr_arr=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr")
                a_tag=tr_arr.select_one('td.td_article > div.board-list > div > a')
                map = {
                "title":a_tag.text.strip(),
                "url":'https://cafe.naver.com' + a_tag["href"],
                "brand": " "
                }
                print(map)
                #sleep(2)
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