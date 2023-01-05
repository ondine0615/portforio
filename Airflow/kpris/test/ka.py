from collections import namedtuple
import pymysql
import requests
import xmltodict
from time import sleep
from datetime import datetime, timedelta
import os
import sys
import redis

par_tuple=namedtuple('parameters',['task_id','requests_url','params','type_'])

test=par_tuple("test_id",'test_url','test_par','test_type')
print(test[0])