from kafka import KafkaConsumer, KafkaProducer
import json

TOPIC_NAME='test'
LOUIS_topic="Louis" #루이비통
DIOR_topic="Dior"  # 디올
PRADA_topic="prada" #프라다
GUGGI_topic="guggi" #구찌
CHANEL_topic="chanel"
HERMES_topic="hermes"
brokers=["localhost:9092"]


consumer=KafkaConsumer(TOPIC_NAME, bootstrap_servers=brokers)
producer=KafkaProducer(bootstrap_servers=brokers)

#{'title': '샤넬 탑핸들 뉴미니', 
# 'url': 'https://cafe.naver.com/ArticleRead.nhn?clubid=10050146&page=1&menuid=782&boardtype=L&articleid=943913557&referrerAllArticles=false',
# 'is_checked': True, 
# 'brand': '샤넬'}

def select_(message):
    
    if message['brand']=='루이비통':
        return  LOUIS_topic
    elif message['brand']=='디올':
        return DIOR_topic
    elif message['brand']=='프라다':
        return PRADA_topic
    elif message['brand']=='구찌':
        return GUGGI_topic
    elif message['brand']=='샤넬':
        return CHANEL_topic
    elif message['brand']=='에르메스':
        return HERMES_topic
    elif message['brand']==' ':
        pass


for message in consumer:
    msg = json.loads(message.value.decode())
    #msg = message.value
    topic = select_(msg) 
    producer.send(topic, json.dumps(msg).encode("utf-8"))
    print(topic, select_(msg), msg)
    producer.flush()