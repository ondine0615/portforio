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


#compare={'url':0}
#is_first=True
target=["에르메스","루이비통","디올","프라다","구찌","샤넬","메종마르지엘라"]
excepts=["삽니다","매입","구매","구입"]
recentSubject=""

my_arr=[]
#BASE_URL="https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=782&search.boardtype=L"

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
                sleep(10)
                continue
            elif recentSubject !=number:
                print("새로운 게시물 갱신")
                recentSubject=number
                #print(f'{recentSubject}와 {number}의 숫자가 다릅니다. 기록을 갱신.')
                tr_arr=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr")
                a_tag=tr_arr.select_one('td.td_article > div.board-list > div > a')
                map = {
                "title":a_tag.text.strip(),
                "url":'https://cafe.naver.com' + a_tag["href"],
                "brand":" "
                }
                
                if any(x in map["title"] for x in target) and not any(x in map["title"] for x in excepts):
                    clean_msg=clean_text(map["title"])
                    msg_split=clean_msg.split(" ")
                    for msg in msg_split:
                        for tar in target:
                            if msg in tar:
                                map["brand"]=msg
                                
                    # for tar in target:
                    #     matching=[s for s in msg_split if tar in s]
                    # if matching==[]:
                    #     map['brand']='None'
                    # else:
                    #     map['brand']=matching
                    print(map)
                    sleep(10)