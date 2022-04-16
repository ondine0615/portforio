import os
import pandas as pd
import re

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
    emotes_df = pd.DataFrame.from_dict(emotes_dict, orient='index')
    emotes_df=emotes_df.T

    # 저장
    csv_name=text.split('.')[0]
    emotes_df.to_csv("/home/ondine0615/airflow/twitch_csv2/{}.csv".format(csv_name),encoding='UTF-8')
    
    chat_data.close()