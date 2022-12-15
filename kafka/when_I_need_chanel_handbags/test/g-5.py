from kafka import KafkaProducer

from bs4 import BeautifulSoup as bs
import re
from time import sleep
import redis 

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
#from requests.packages.urllib3.util.retry import Retry
import json

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

rd=redis.StrictRedis(host='127.0.0.1',port=6379,db=2)
url="http://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=334&search.boardtype=L"
TOPIC_NAME="test"
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.207 Whale/3.17.145.18 Safari/537.36'}



def requests_retry_session(retries=10,
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
    res=requests_retry_session().get(target_page,headers=headers)
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
        target_brand='apple'
    elif '삼성' in text or '갤럭시' in text or 'galaxy' in text:
        target_brand='samsung'
    elif '엘지' in text or 'LG' in text or '그램' in text or 'gram' in text:
        target_brand='lg'
    elif '아수스' in text or "에이수스" in text or "ASUS" in text or "asus" in text:
        target_brand='asus'
    elif 'dell' in text or '델' in text or "DELL" in text:
        target_brand='dell'
    elif '한성' in text:
        target_brand='hansung'
    elif 'HP' in text or 'hp' in text:
        target_brand='HP'
    elif '레노버' in text or 'lenovo' in text or 'thinkpad' in text:
        target_brand='lenovo'
    else:
        target_brand='etc'
    return target_brand  

def map_the_dict():
    #with requests_retry_session.Session() as s:
    res=requests_retry_session().get(url,headers=headers)
    if res.status_code==requests.codes.ok:
        par_soup=bs(res.text, 'html.parser')
        tr_arr=par_soup.select_one("#main-area > div:nth-child(4) > table > tbody > tr")
        a_tag=tr_arr.select_one('td.td_article > div.board-list > div > a')
        map = {
        "title":a_tag.text.strip(),
        "url":'https://cafe.naver.com' + a_tag["href"],
        "brand":brand_sorting(a_tag.text.strip()),
        }
        map['price']=find_price(map['url'])
        #map=json.dumps(map)
        return map
    else:
        print("mapping request error!!!")

def find_price(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')    
    driver = webdriver.Chrome(executable_path='./chromedriver',options=chrome_options)
    try:
        driver.get(url)
        driver.implicitly_wait(3)
        p_tag = WebDriverWait(driver,timeout=20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="cafe_main"]')))
        driver.switch_to.frame(p_tag)
        sleep(5)
        src=driver.page_source
        #sleep(10)
        soup=bs(src,'html.parser')
        comma_del=clean_text(soup.find('div',class_='ProductPrice').text)
        
        #return comma_del.replace('원','')
        if comma_del == None:
            return int('0')
        else:
            return int(comma_del.replace('원',''))
    except:
        print("cannot pull info, anyway.. do continue")
        pass
    
def kafka_connect(TOPIC_NAME,data):
    #brokers=["localhost:9091","localhost:9092","localhost:9093"]
    brokers=["localhost:9092"]
    producer = KafkaProducer(bootstrap_servers=brokers)
    producer.send(TOPIC_NAME, json.dumps(data).encode("utf-8"))
    producer.flush()

def numbering(table_number):
    if rd.sismember('done',table_number)==1:
        print('there is no new item')
        sleep(10)
    elif rd.sismember('done',table_number)==0:
        rd.delete('done')
        rd.sadd('done',table_number)
        print('start producing')
        print(map_the_dict())
    
while True:
    
    try:
        numbering(get_table_number(url))
    except requests.exceptions.ConnectionError:
        count=0
        count+=1
        print(f"접속 차단->>>>>>>>>{count}번째 재접속 시도 중->>>>>>>>..")
        sleep(5*count)
        pass
        #numbering(get_table_number(url))
                
    kafka_connect(TOPIC_NAME,map_the_dict())
    sleep(15)
