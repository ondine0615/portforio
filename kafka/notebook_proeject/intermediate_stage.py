from kafka import KafkaConsumer, KafkaProducer
import json

TOPIC_NAME='test'
SAMSUNG_topic="samsung"
APPLE_topic="apple"  
HP_topic="HP" 
HANSUNG_topic="hansung" 
DELL_topic="dell"
ASUS_topic="asus"
LENOVO_topic="lenovo"
LG_topic="lg"

def select_(message):
    
    if message['brand']=='samsung':
        return  SAMSUNG_topic
    elif message['brand']=='apple':
        return APPLE_topic
    elif message['brand']=='HP':
        return HP_topic
    elif message['brand']=='hansung':
        return HANSUNG_topic
    elif message['brand']=='dell':
        return DELL_topic
    elif message['brand']=='asus':
        return ASUS_topic
    elif message['brand']=='lenovo':
        return LENOVO_topic
    elif message['brand']=='lg':
        return LG_topic

brokers=["localhost:9092"]
consumer=KafkaConsumer(TOPIC_NAME, bootstrap_servers=brokers)

producer=KafkaProducer(bootstrap_servers=brokers)

for message in consumer:
    msg = json.loads(message.value.decode())
    #msg = message.value
    #TOPIC = select_(msg) 
    TOPIC=select_(msg)
    producer.send(TOPIC, json.dumps(msg).encode("utf-8"))
    #producer.send(TOPIC_NAME, json.dumps(msg).encode("utf-8"))
    print(TOPIC, select_(msg), msg)
    producer.flush()