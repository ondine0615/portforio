import pymysql
import requests
import xmltodict
import time
from datetime import datetime, timedelta
import os
import sys
import redis

redis_ = redis.StrictRedis(host='127.0.0.1',port=6379, db=2, charset="utf-8",decode_responses=True)

service_info = {'task_id' : "registrationInfo",
                 'url':'http://plus.kipris.or.kr/openapi/rest/RegistrationService/',
                 'params':['registrationNumber','accessKey'],
                'type_':'reg',
                'key' : 'accessKey',
                'date' : 'transferDate',
                'searchType':'BIB'
                }
api_key = "Y74vSqogy7fkw71F26g146N4s9Harc7sLqm4ONkWHWE="



work_date=list(redis_.smembers("work_date"))

params={}

url = service_info['url']

service_info['api_key'] = api_key
params[f"{service_info['key']}"] =service_info['api_key']

searchType=service_info['searchType']
params['searchType']=searchType
print(params)

today_str=datetime.now()-timedelta(20)
today_str=int(today_str.strftime('%Y%m%d'))
print(today_str)

work_date=list(redis_.smembers("work_date"))
transDate=list(work_date)[0]

params[f"{service_info['date']}"]=transDate

# '20220913'
print(params)

re=requests.get(service_info['url'],params)
print(re)