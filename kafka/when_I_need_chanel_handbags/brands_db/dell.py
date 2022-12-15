from kafka import KafkaConsumer
import json
from datetime import datetime
import pymysql

#TOPIC_NAME='test'



dell_topic="dell"
#brokers = ["localhost:9091","localhost:9092",'localhost:9093']
brokers=["localhost:9092"]
consumer = KafkaConsumer(dell_topic,bootstrap_servers=brokers,
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='my-group',
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

conn = pymysql.connect(host='127.0.0.1',
                        user='root',
                        password='rotin11',
                        db="kafka",
                        port= 3306,
                        charset='utf8'
                        )
cursor = conn.cursor()

create_query="""CREATE TABLE IF NOT EXISTS dell (title text,url text,price integer)"""
cursor.execute(create_query)
conn.commit()

for message in consumer:
    msg = message.value
    title=msg['title']
    url=msg['url']
    date = datetime.now().strftime("%Y-%m-%d")
    #query = "INSERT INTO chanel5 (title,url,date) VALUES (%s,%s,%s)",(title, url, date)
    cursor.execute("INSERT IGNORE INTO dell (title,url,date) VALUES (%s,%s,%s)",(title, url, date))
    #cursor.execute(query)
    conn.commit()

    
    #cursor.execute(sql, (msg["title"],msg["url"]))
    print(title, url, date)
    
conn.close()