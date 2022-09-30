from kafka import KafkaConsumer
import json
from datetime import datetime
import psycopg2

consumer = KafkaConsumer(
    'test',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: json.loads(x.decode('utf-8')))

conn = psycopg2.connect( database="OSLO_CITY_Bike", user='postgres', password='password', host='127.0.0.1', port= '5432')
cursor = conn.cursor()

for message in consumer:
    message = message.value
    
    #print(message['last_updated'])
    #timestamp = message['last_updated']
    #dt_object = datetime.fromtimestamp(timestamp)
    #print(dt_object)

    timestamp = message['last_updated']
    #message=json.loads(message.value.decode())
    #timestamp=message['last_updated']
    dt_object = datetime.fromtimestamp(timestamp)
    message['Date'] = dt_object.strftime("%b %d %Y %H:%M:%S")
    datehrs = dt_object.strftime("%b %d %Y %H:%M:%S")
    for station in message['data']['stations']:
        cursor.execute("INSERT INTO Station_Status (Station_id,is_installed, is_renting, is_returning,last_reported,num_bikes_available,num_docks_available,date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", 
                       (station['station_id'],
                        station['is_installed'],
                        station['is_renting'],
                        station['is_returning'],
                        station['last_reported'],
                        station['num_bikes_available'],
                        station['num_docks_available'],
                        dt_object))
        conn.commit()
    print('Data at {} added to POSTGRESQL'.format(dt_object))
    #print('Data at {} added to POSTGRESQL'.format(dt_object, collection))

conn.close()

