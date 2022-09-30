import redis


import subprocess
import glob
import os
import warnings
warnings.filterwarnings(action="ignore")

import re
import requests 
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import pandas as pd
display = Display(visible=0, size=(1920, 1080)) 
display.start() 



class Twtich(object):
    rd=redis.StrictRedis(host="127.0.0.1",port=6379,db=1,charset="utf-8",decode_responses=True)
    # VOD의 ID를 추출, 
    def extract_from_website(self):
                    
        path="/home/ondine0615/workplace/chat-log/chromedriver"
        driver = webdriver.Chrome(path)

        driver.get("https://www.twitchmetrics.net/c/49045679-woowakgood/videos?sort=published_at-desc")
        #col=driver.find_element_by_class_name("col-9") deprived
        col = driver.find_element(By.CLASS_NAME, 'col-9')
        
        tag_=col.find_element(By.TAG_NAME, 'a')
        
        #_href=col.find_element_by_tag_name("a") deprived
        #link_=_a.get_attribute('href')
        #_id=_link_.split('/')[4]

        link_=tag_.get_attribute('href')
        href_=link_.split('/')[-1] ##1594329272

        #time=driver.find_element_by_class_name("time_ago")
        time=driver.find_element(By.CLASS_NAME, "time_ago")
        _date=time.get_attribute("datetime")
        broad_day=_date.split('T')[0]

        subprocess.run(f"/home/ondine0615/workplace/chat-log/data/TwitchDownloaderCLI -m ChatDownload --id {href_} --timestamp-format Relative -o {broad_day}.txt",shell=True)
    
    def emontion_count_one(self):
        # 수집
        path="/home/ondine0615/workplace/chat-log/data"
        file_list=os.listdir(path)
        file_list_text=[file for file in file_list if file.endswith(".txt")]

        file_list_text.sort()
        latest_file=file_list_text[-1] #정렬 후 가장 마지막 -> 가장 최신의 파일 

        chat_data=open('/home/ondine0615/workplace/chat-log/data/{}'.format(latest_file),'r')

        chat_data_line=chat_data.read()
        chat_data_line_split=chat_data_line.splitlines()

        # preprocess
        wak_count=[]
        wak=re.compile("wak[a-zA-Z0-9]*")
        
        for chat in chat_data_line_split:
            find_wak=wak.findall(chat)
            if len(find_wak)==0: # 이모티콘을 사용하지 않은 채팅 내역은 배제한다. 
                pass
            else:
                wak_count.append(find_wak)
                
            ####----2차 필터링 : 과대표집을 억제한다. 
        list_one=sum(wak_count,[])
        result=[]
        for i in list_one:
            aa=i.split()[0]
            result.append(aa)
            
            ####----3차 필터링 : 기타 노이즈를 제거한다. 
        filter_list=['wakAegood','wakAh','wakAk','wakApple'
                    ,'wakArgt','wakBab','wakBbak',
                    'wakBong','wakCheck','wakChok','wakCold',
                    'wakCu2','wakCut','wakCyder','wakDb',
                    'wakDc','wakDoor','wakEe',' akEnha',
                    'wakF','wakGalaxy','wakGc','wakGgm',
                    'wakGt','wakHc','wakHi','wakHm','wakJ1',
                    'wakJ2','wakJ3',' akJa','wakJjch','wakJjub',
                    'wakJjup','wakKa','wakKeep','wakKmc',
                    'wakLe','wakLoyal','wakMaegood','wakMc',
                    'wakMg','wakMs','wakMs2','wakMv',
                    'wakNana','wakOba3','wakRe',
                    'wakSb','wakSd','wakSh','wakSing','wakSkip',
                    'wakSlow','wakSon2',' wakSs','wakSsh','wakWango','wakZanzan',
                    'wakChobbak','wakGek','wakLpc',
                    'wakOba2','wakYs','wakFighting','wakGp','wakGwan','wakMp',
                    'wakWh','wakCu','wakGj','wakLegeno2','wakSad','wakSeul']

        emotes_list=[]
        for emotes in result:
            if emotes in filter_list:
                emotes_list.append(emotes)
            else:
                pass
        emotes_dict={}
        for v in emotes_list:
            if emotes_dict.get(v): emotes_dict[v] +=1
            else: emotes_dict[v]=1
        emotes_df = pd.DataFrame.from_dict(emotes_dict, orient='index',columns=['count'])


        # 저장
        csv_name=latest_file.split('.')[0]
        emotes_df.to_csv("/home/ondine0615/airflow/twitch_csv/{}.csv".format(csv_name),encoding='UTF-8')
        chat_data.close()
            
    def emotion_count_all(self):
        
        redis_=self.rd()
        path="/home/ondine0615/workplace/chat-log/data"
        file_list=os.listdir(path)
        file_list_text=[file for file in file_list if file.endswith(".txt")]
        file_list_text.sort()

        for text in file_list_text:
            chat_data=open('/home/ondine0615/workplace/chat-log/data/{}'.format(text),'r')
            chat_data_line=chat_data.read()
            chat_data_line_split=chat_data_line.splitlines()
            # preprocess : 1차 필터링 - 이모티콘을 사용한 채팅만 재배치 
            wak_count=[]
            wak=re.compile("wak[a-zA-Z0-9]*")
            for chat in chat_data_line_split:
                find_wak=wak.findall(chat)
                if len(find_wak)==0: # 이모티콘을 사용하지 않은 채팅 내역은 배제한다. 
                    pass
                else:
                    wak_count.append(find_wak) 
            list_one=sum(wak_count,[])
                
                ##---- preprocess(2) : 특정 이모티콘의 과대표집을 방지하기 위해 가장 먼저 사용한 이모티콘만 count한다. 
            result=[]
            for i in list_one:
                aa=i.split()[0]
                result.append(aa)

                ##---- preprocess(3) : 

            filter_list=['wakAegood','wakAh','wakAk','wakApple',
                        'wakArgt','wakBab','wakBbak',
                        'wakBong','wakCheck','wakChok','wakCold',
                        'wakCu2','wakCut','wakCyder','wakDb',
                        'wakDc','wakDoor','wakEe','wakEnha',
                        'wakF','wakGalaxy','wakGc','wakGgm',
                        'wakGt','wakHc','wakHi','wakHm','wakJ1',
                        'wakJ2','wakJ3','wakJa','wakJjch','wakJjub',
                        'wakJjup','wakKa','wakKeep','wakKmc',
                        'wakLe','wakLoyal','wakMaegood','wakMc',
                        'wakMg','wakMs','wakMs2','wakMv',
                        'wakNana','wakOba3','wakRe',
                        'wakSb','wakSd','wakSh','wakSing','wakSkip',
                        'wakSlow','wakSon2','wakSs','wakSsh','wakWango','wakZanzan',
                        'wakChobbak','wakGek','wakLpc',
                        'wakOba2','wakYs','wakFighting','wakGp','wakGwan','wakMp',
                        'wakWh','wakCu','wakGj','wakLegeno2','wakSad','wakSeul']

            emotes_list=[]
            for emotes in result:
                if emotes in filter_list:
                    emotes_list.append(emotes)
                else:
                    pass
                
            emotes_dict={}
            for v in emotes_list:
                if emotes_dict.get(v): emotes_dict[v] +=1
                else: emotes_dict[v]=1
            
            for emotes in emotes_dict:
                redis_.delete(f'{emotes}',emotes_dict[f'{emotes}'])
                redis_.sadd(f'{emotes}',emotes_dict[f'{emotes}'])
            
            
            
            
            # emotes_df = pd.DataFrame.from_dict(emotes_dict, orient='index')
            # emotes_df=emotes_df.T

            # # 저장
            # csv_name=text.split('.')[0]
            # emotes_df.to_csv("/home/ondine0615/airflow/twitch_csv2/{}.csv".format(csv_name),encoding='UTF-8')
            
            # chat_data.close()
    
    
    
    # def concat_all_csv(self):

    #     files_2=os.path.join("/home/ondine0615/airflow/twitch_csv2/*.csv")
    #     files_list_2=glob.glob(files_2)

    #     df_3=pd.concat(map(pd.read_csv, files_list_2),ignore_index=True,sort=False)
    #     df_3=df_3.fillna('0')
    #     df_3=df_3.astype(int)
    #     df_3=df_3.drop("Unnamed: 0",axis=1)

    #     df_sum=df_3.sum().sort_index()
    #     df_sum.to_csv("/home/ondine0615/workplace/chat-log/csv/df_sum.csv",header=False)
        
        
    