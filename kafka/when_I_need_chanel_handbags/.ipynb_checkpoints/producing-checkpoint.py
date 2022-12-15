from kafka import KafkaProducer
import requests
from bs4 import BeautifulSoup as bs
import re
from time import sleep
import json
import os

class Ine(object):
    def __init__(self):
        self.target=["에르메스","루이비통","디올","프라다","구찌","샤넬"]
        self.excepts=["삽니다","매입","구매","구입"]
        self.recentSubject=""
        self.TOPIC_NAME="test"
        self.BASE_URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
        #self.producer=KafkaProducer(bootstrap_servers=brokers)
        #self.brokers=["localhost:9092"]
        
    def clean_text(self,text):
            cleaned_text = re.sub('[a-zA-Z]','',text)
            cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', cleaned_text)
            return cleaned_text
        
    def notify(self,title, text):
    # loop = asyncio.get_event_loop()
    # loop.run_in_executor(None, os.system, f"""
    #     osascript -e 'tell app "System Events" to display dialog "{title}"'
    # """)
        os.system(f"""
            osascript -e 'display notification "{title}" with title "{text}"'
            """)
        os.system(f'say "{title}"')
    
    def data_collect(self):

        with requests.Session() as s:
            #BASE_URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"
            res=s.get(self.BASE_URL)
            if res.status_code==requests.codes.ok:
                par_soup=bs(res.text, 'html.parser')
                number=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr:nth-child(1) > td.td_article > div.board-number > div").text

                if self.recentSubject==number:
                    print('there is no new product')

                    sleep(3)
                    
                elif self.recentSubject !=number:
                    self.recentSubject=number
                    print(self.recentSubject,"new number -> start preprocessing")
                    sleep(2)
                    tr_arr=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr")
                    a_tag=tr_arr.select_one('td.td_article > div.board-list > div > a')
                    map = {
                    "title":a_tag.text.strip(),
                    "url":'https://cafe.naver.com' + a_tag["href"],
                    "brand": " "
                    }
                    #print(map)
                    #sleep(2)
                if any(x in map["title"] for x in self.target) and not any(x in map["title"] for x in self.excepts):
                    msg_split=self.clean_text(map["title"]).split(" ")
                    for msg in msg_split:
                        for tar in self.target:
                            val = msg.find(tar)
                            if val !=-1:
                                map['brand']=tar
                                print("intermediate_stage.py로 데이터 전송, index:", val)
                                print(map)
#                                sleep(3)
                    

if __name__ == '__main__':
    try:
        vo=Ine()
        while True:
            print(vo.recentSubject)
            sleep(3)
        main()
    except Exception as e:
        print(e)
        vo.notify('오류 발생', e)



vo = Ine()
while True:
    #print(vo.data_collect())
    print(vo.recentSubject)
    sleep(3)
 #       print(map)
        #brokers=["localhost:9092"]
        #producer = KafkaProducer(bootstrap_servers=brokers)
        
        #producer.send(vo.TOPIC_NAME, json.dumps(map).encode("utf-8"))
        #producer.flush()
        #print(map)

