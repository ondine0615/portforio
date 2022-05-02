import csv, requests
import pandas as pd

CSV_URL="https://raw.githubusercontent.com/jooeungen/coronaboard_kr/master/kr_regional_daily.csv"

region=["서울","부산","대구","인천","광주","대전","울산","세종","경기","강원","충북","충남","전북","전남","경북","경남","제주","검역",]

past_data={}
for i in region:
    past_data[i]=[0,0,0] # 확진, 사망, 격리해제 순, ictionary 형태로 받아온다. 

flag=False
corona_data=[]

with requests.Session() as s:
    download = s.get(CSV_URL) 
    decoded_content=download.content.decode("utf-8")
    csv_read=csv.reader(decoded_content.splitlines(),delimiter=',')
    my_list=list(csv_read)
    
    for row in my_list:
        if row[0] =='date':
            continue
        #증가분만 처리하는게 맞는 것 같다. 
        for j in range(2,5):
            row[j]=int(row[j]) - int(past_data[row[1]][j-2])
        #
        for x in range(3):
            past_data[row[1]][x]+=row[x+2]

            
        corona_data.append(row)
        
df=pd.DataFrame(corona_data)

df.to_csv("covid_korea.csv",index=False,header=False,encoding="utf8")
