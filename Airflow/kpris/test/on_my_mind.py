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

class Kipris(object):
    
    def __init__(self):
        
        # DB setting
            # redis
        self.redis=redis.StrictRedis(host='127.0.0.1',port=6379,db=3,decode_responses=True)
        self.api_key = "Y74vSqogy7fkw71F26g146N4s9Harc7sLqm4ONkWHWE="
        self.conn_data = {
            'host' : '127.0.0.1',
            'port' : 3306,
            'user': 'root',
            'password':'rotin11',
            'database': "아직없음"
        }
        # mysql_patent_table
        self.conn_data_patent= None
        
        
        #Logger setting
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger=logging.FileHandler('./error_logs/err_output.log')
        self.logger.setFormatter(self.formatter)
        #self.logger.addHandler(self.logger)
        
        
        
        # data list setting
        self.list_services=namedtuple('list_services',
                                      ['task_id','url','type','searchType','key','date'])
        
        self.bib=self.list_services("registrationTransferListInfo",
                          'http://plus.kipris.or.kr/openapi/rest/RegistrationService/',
                          'reg',
                          'BIB',
                          self.api_key,
                          (datetime.datetime.now()-datetime.timedelta(10)).strftime('%Y%m%d'))

        self.ord=self.list_services("registrationTransferListInfo",
                          'http://plus.kipris.or.kr/openapi/rest/RegistrationService/',
                          'reg',
                          'ORD',
                          self.api_key,
                          (datetime.datetime.now()-datetime.timedelta(10)).strftime('%Y%m%d'))

        self.hld=self.list_services("registrationTransferListInfo",
                          'http://plus.kipris.or.kr/openapi/rest/RegistrationService/',
                          'reg',
                          'HLD',
                          self.api_key,
                          (datetime.datetime.now()-datetime.timedelta(10)).strftime('%Y%m%d'))
        
        self.searchtype_services=[self.bib,self.ord,self.hld]
    
    
    # params setting
    def get_searchtype(self):
        task_id_list=[]    
        tmp_app_list=[]
        for services in self.searchtype_services:
            target_url=f"{services.url}/{services.task_id}?transferDate={services.date}&searchType{services.searchType}&accessKey={services.key}"
            content_dict=self.item_check(target_url,low_level=True)
            print(content_dict)
    def request_get(self,url):
        try:
            requests.get(url=url)        
        except:
            self.logger.setFormatter(self.formatter)
            
            

    def item_check(self,url,low_level=False):
        try:
            response = self.request_get(url)
            content_xml=response.content
            print(content_xml)
                
            key_name=list(xmltodict.parse(content_xml)['response']['body'][0])
            content=xmltodict.parse(content_xml)['response']['body'][f'{key_name}']
            
            if content is None:
                return []
            else:
                if low_level:
                    return content 
                # low_level이 True인 경우, ['body]['*']['*']까지만 진입
                detail_name=list(content)[0]
                content=content[detail_name]
                return content
                # low_level이 false인 경우, ['body']['*']['*']['*']까지 진입
        except:
            self.logger.setFormatter(self.formatter)

                
if __name__ == '__main__':
    run = Kipris()
    print(run.get_searchtype())

