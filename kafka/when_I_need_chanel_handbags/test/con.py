from kafka import KafkaConsumer, KafkaProducer
import json
import time
TOPIC_NAME='test'
LOUIS_topic="Louis" #루이비통
DIOR_topic="Dior"  # 디올
PRADA_topic="prada" #프라다
GUGGI_topic="guggi" #구찌
chanel_topic="chanel"
brokers=["localhost:9091","localhost:9092","localhost:9093"]


consumer=KafkaConsumer(TOPIC_NAME, bootstrap_servers=brokers)
producer=KafkaProducer(bootstrap_servers=brokers)

# def bagmaker(map):
#     if map["title"] == ""

for message in consumer:
    msg=json.loads(message.value.decode())
    print(msg)
    time.sleep(1) 