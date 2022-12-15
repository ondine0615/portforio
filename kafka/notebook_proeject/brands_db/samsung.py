from kafka import KafkaConsumer
import json
#from datetime import datetime
import pymysql

#TOPIC_NAME='test'


TOPIC_NAME='samsung'
#brokers=["localhost:9091","localhost:9092","localhost:9093"]
brokers=["localhost:9092"]
consumer = KafkaConsumer(TOPIC_NAME,bootstrap_servers=brokers,
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

create_query="""CREATE TABLE IF NOT EXISTS samsung (title text,url text,price int(7))"""
cursor.execute(create_query)
conn.commit()

for message in consumer:
    msg = message.value
    title=msg['title']
    url=msg['url']
    price=msg['price']    
    cursor.execute("INSERT IGNORE INTO samsung (title,url,price) VALUES (%s,%s,%s)",(title, url, price))
    conn.commit()
    print(title, url, price)
    
conn.close()