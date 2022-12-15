from kafka import KafkaConsumer
import json
#from datetime import datetime
import pymysql

#TOPIC_NAME='test'



TOPIC="test2"
brokers = ["localhost:9091","localhost:9092",'localhost:9093']
consumer = KafkaConsumer(TOPIC,bootstrap_servers=brokers,
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id='my-group',)
                         #value_deserializer=lambda x: json.loads(x.decode('utf-8')))

conn = pymysql.connect(database="database_name",
                        user='postgres',
                        password='password',
                        host='127.0.0.1',
                        port= '5432')
cursor = conn.cursor()

create_query="""CREATE TABLE IF NOT EXISTS test01_info (title text,url text,price text)"""
cursor.execute(create_query)
conn.commit()

while True:
    try:
        for message in consumer:
            #msg = message.value
            msg = json.loads(message.value.decode())
            title=msg['title']
            url=msg['url']
            price=msg['price']
            #cursor.execute("INSERT IGNORE INTO products_info (title,url,price) VALUES (%s,%s,%s)",(title, url, price))
            cursor.execute("INSERT INTO test01_info (title,url,price) VALUES (%s,%s,%s)",(title, url, price))
            conn.commit()
            print(title, url, price)
            conn.close()
    except:
        pass
