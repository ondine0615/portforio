from time import sleep
from json import dumps
from kafka import KafkaProducer
import requests

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8'))

for i in range(120): #60 Minutes
    headers = {
        'Client-Identifier': 'dan-citymonitor',
    }

    response = requests.get('https://gbfs.urbansharing.com/oslobysykkel.no/station_status.json', headers=headers)
    r = response.json()
    producer.send('test', value=r)
    print(r)
    sleep(30)