"""
 --packages 이하 부분에서는 사용하시는 프로그램의 버전을 맞춰야 합니다.   
 spark streaming 프로그램과 kafka를 연결하기 위한 매개체를 kafka 폴더 내에 넣어야 합니다. jar 형식으로 되어있습니다. 
  1. kafka-clients-2.6.0.jar
  2. spark-sql-kafka-0-10_2.12-3.1.1.jar
  3. spark-token-provider-kafka-0-10_2.12-3.1.1.jar 
  사용하는 버전에 맞춰 다른 jar 파일을 wget으로 spark/jars 폴더 내에 넣어주셔야 합니다. 
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import os
import findspark
findspark.init()


  
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell'

spark=SparkSession.builder.appName('twitch-chat-stream').master("local").getOrCreate()

kafka_df=spark.readStream.format("kafka").option("kafka.bootstrap.servers","9092").option("subscribe","chat-log").option("startingOffsets", "earliest").load()

query = kafka_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .writeStream \
    .format("console") \
    .option("partition.assignment.strategy","org.apache.kafka.clients.consumer.RangeAssignor")\
    .option("checkpointLocation", "path/to/HDFS/dir") \
    .start()
    
query.awaitTermination()

#현 상황
"""
Missing required configuration "partition.assignment.strategy" which has no default value.
=== Streaming Query ===
Identifier: [id = e04c8d54-2dcf-4162-b083-22edfdefcc01, runId = e3453b92-0cd7-4be8-af8e-4149da5e87b7]
Current Committed Offsets: {}
Current Available Offsets: {}


이건 대체 왜 생기는 에러인걸까... 
"""
