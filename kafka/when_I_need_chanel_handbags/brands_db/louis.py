from kafka import KafkaConsumer
import json
from datetime import datetime
import psycopg2

#TOPIC_NAME='test'



LOUIS_topic="louis"
brokers = ["localhost:9091","localhost:9092",'localhost:9093']
consumer = KafkaConsumer(LOUIS_topic,bootstrap_servers=brokers,
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='my-group',
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

conn = psycopg2.connect(database="kafka",
                        user='postgres',
                        password='password',
                        host='127.0.0.1',
                        port= '5432')
cursor = conn.cursor()

create_query="""CREATE TABLE IF NOT EXISTS louis (title text,url text,date date)"""
cursor.execute(create_query)
conn.commit()

for message in consumer:
    msg = message.value
    title=msg['title']
    url=msg['url']
    date = datetime.now().strftime("%Y-%m-%d")
    #query = "INSERT INTO chanel5 (title,url,date) VALUES (%s,%s,%s)",(title, url, date)
    cursor.execute("INSERT INTO louis (title,url,date) VALUES (%s,%s,%s)",(title, url, date))
    #cursor.execute(query)
    conn.commit()

    
    #cursor.execute(sql, (msg["title"],msg["url"]))
    print(title, url, date)
    
conn.close()