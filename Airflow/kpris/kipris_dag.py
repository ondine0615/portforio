import sys
import os
import pymysql
import xmltodict
import redis
import requests
#from datetime import datetime
import datetime
from collections import namedtuple
import logging
from time import sleep
import time

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pendulum
from kipris_plus import Kipris
local_tz=pendulum.timezone("Asia/Seoul")

kipris=Kipris()

default_args = {
    'owner':'Airflow',
    'depends_on_past':False,
    'start_date':datetime(2023,1,1,0,0,tzinfo=local_tz),
    'catchup':False,
    'retries':12,
    'retry_delay':timedelta(minutes=10),
    'provide_context':True
}

def init_date(**kwargs):
    redis=redis.StrictRedis(host="127.0.0.1",port=6379, db=3, decode_responses=True)
    
    today_str=kwargs['execution_date'].strftime('%Y%m%d')
    redis.delete('work_date')
    redis.sadd('work_date',today_str)

kipris_delta1day=DAG(
    dag_id="KIPRIS_API",
    default_args=default_args,
    max_active_runs=1,
    schedule=timedelta(days=1)
)
init_working=PythonOperator(
    task_id="init_working",
    python_callable=init_date,
    dag=kipris_delta1day
)
get_searchtype=PythonOperator(
    task_id='get_searchtype',
    python_callable=kipris.get_searchtype,
    dag=kipris_delta1day
)
process_working=PythonOperator(
    task_id='process_working',
    python_callable=kipris.process_working,
    op_kwargs={'list_type':'reg'},
    dag=kipris_delta1day
)

init_working >> get_searchtype >> process_working