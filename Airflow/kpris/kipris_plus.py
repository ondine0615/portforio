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

class Kipris(object):
    
    def __init__(self):
        
        # DB setting
            # redis
        self.redis=redis.StrictRedis(host='127.0.0.1',port=6379,db=3,decode_responses=True)
        self.api_key = "Y74vSqogy7fkw71F26g146N4s9Harc7sLqm4ONkWHWE="
        #mysql_reg_database(등록번호 기반)
        self.conn_data = {
            'host' : '127.0.0.1',
            'port' : 3306,
            'user': 'root',
            'password':'rotin11',
            'database': "KIPRIS"
        }
        # mysql_patent_database(출원번호 기반; 예정)
        self.conn_data_patent= None
        {
            'host':'127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'rotin11',
            'database': 'patent'
        }
        
        
        #Logger setting
        #self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #self.logger=logging.FileHandler('./error_logs/err_output.log',mode='w')
        #self.logger.setFormatter(self.formatter)
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
        
        self._many={}    

        # mysql query
        self.app_from_reg= """
        select applicationNumber
        from KIPO_ADMIN_BIBLIOGRAPHIC
        where registerNumber = %s
        """
        self.rightHolderA_query = """
        INSERT INTO REGISTRATION_RIGHT_HOLDER_A(
            RANK_NUMBER,
            RANK_CORRELATOR_SERIAL_NUMBER,
            RANK_CORRELATOR_TYPE,
            RANK_CORRELATOR_NAME,
            RANK_CORRELATOR_ADDRESS,
            REGISTRATION_NUMBER,
            TRANSFER_DATE
        )
        VALUES (%s, %s, %s, %s, %s,%s, %s)
        ON DUPLICATE KEY UPDATE
            RANK_CORRELATOR_NAME = VALUES(RANK_CORRELATOR_NAME),
            RANK_CORRELATOR_ADDRESS= VALUES(RANK_CORELATOR_ADDRESS),
            TRANSFER_DATE=VALUES(TRANSFER_DATE),
            MOD_DT=SYSDATE()
        """
        self.rightHolderB_query="""
        INSERT INTO REGISTRATION_RIGHT_HOLDER_B (
            RANK_NUMBER,
            DOCUMENT_NAME,
            RECEIPT_DATE,
            REGISTRATION_CAUSE_NAME,
            INDECATION_OF_EVENT,
            REGISTRATION_NUMBER,
            TRANSFER_DATE            
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            DOCUMENT_NAME = VALUES(DOCUMENT_NAME),
            RECEIPT_DATE = VALUES(RECEIPT_DATE),
            REGISTRATION_CAUSE_NAME = VALUES(REGISTRATION_CAUSE_NAME),
            INDICATION_OF_EVENT = VALUES(INDICATION_OF_EVENT),
            TRANSFER_DATE = VALUES(TRANSFER_DATE),
            MOD_DT=SYSDATE()
        """
        
        self.rightRank_query = """
        INSERT INTO REGISTRATION_RIGHT_RANK (
            RANK_NUMBER
            , PERTINENT_PARTITION
            , DOCUMENT_NAME
            , ORIGINAL_REGISTRATION_NUMBER
            , REGISTRATION_PURPOSE
            , REGISTRATION_DATE
            , REGISTRATION_CAUSE_NAME
            , REGISTRATION_CAUSE_DATE
            , RECEIPT_NUMBER
            , RECEIPT_DATE
            , DISAPPEARANCE_FLAG
            , DISAPPEARANCE_CAUSE_NAME
            , DISAPPEARANCE_DATE
            , INTERNATIONAL_REG_RECORD_DATE_MD
            , EXPIRATION_DATE_MD
            , LATEST_RENEWAL_DATE_MD
            , SUB_DESIGNATION_DATE_MD
            , REGISTRATION_NUMBER
            , TRANSFER_DATE
            )
        VALUES (%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        DOCUMENT_NAME = VALUES(DOCUMENT_NAME)
        , ORIGINAL_REGISTRATION_NUMBER = VALUES(ORIGINAL_REGISTRATION_NUMBER)
        , REGISTRATION_PURPOSE = VALUES(REGISTRATION_PURPOSE)
        , REGISTRATION_DATE = VALUES(REGISTRATION_DATE)
        , REGISTRATION_CAUSE_NAME = VALUES(REGISTRATION_CAUSE_NAME)
        , REGISTRATION_CAUSE_DATE = VALUES(REGISTRATION_CAUSE_DATE)
        , RECEIPT_NUMBER = VALUES(RECEIPT_NUMBER)
        , RECEIPT_DATE = VALUES(RECEIPT_DATE)
        , DISAPPEARANCE_FLAG = VALUES(DISAPPEARANCE_FLAG)
        , DISAPPEARANCE_CAUSE_NAME = VALUES(DISAPPEARANCE_CAUSE_NAME)
        , DISAPPEARANCE_DATE = VALUES(DISAPPEARANCE_DATE)
        , INTERNATIONAL_REG_RECORD_DATE_MD = VALUES(INTERNATIONAL_REG_RECORD_DATE_MD)
        , EXPIRATION_DATE_MD = VALUES(EXPIRATION_DATE_MD)
        , LATEST_RENEWAL_DATE_MD = VALUES(LATEST_RENEWAL_DATE_MD)
        , SUB_DESIGNATION_DATE_MD = VALUES(SUB_DESIGNATION_DATE_MD)
        , TRANSFER_DATE = VALUES(TRANSFER_DATE)
        , MOD_DT = SYSDATE()
        """
        self.rightholder_info = '''
        INSERT INTO RIGHT_HOLDER (
            PERTINENT_PARTITION
            , RANK_NUMBER
            , REGISTRATION_DATE
            , RANK_CORRELATOR_SERIAL_NUMBER
            , RANK_CORRELATOR_NUMBER
            , RANK_CORRELATOR_TYPE
            , RANK_CORRELATOR_NAME
            , RANK_CORRELATOR_ADDRESS
            , TRANSFER_DATE
            , REGISTRATION_NUMBER
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            REGISTRATION_NUMBER = VALUES(REGISTRATION_NUMBER)
            , PERTINENT_PARTITION = VALUES(PERTINENT_PARTITION)
            , RANK_CORRELATOR_TYPE = VALUES(RANK_CORRELATOR_TYPE)
            , RANK_CORRELATOR_SERIAL_NUMBER = VALUES(RANK_CORRELATOR_SERIAL_NUMBER)
            , RANK_NUMBER = VALUES(RANK_NUMBER)
            , RANK_CORRELATOR_NAME = VALUES(RANK_CORRELATOR_NAME)
            , RANK_CORRELATOR_ADDRESS = VALUES(RANK_CORRELATOR_ADDRESS)
            , RANK_CORRELATOR_NUMBER = VALUES(RANK_CORRELATOR_NUMBER)
            , REGISTRATION_DATE = VALUES(REGISTRATION_DATE)
            , TRANSFER_DATE = VALUES(TRANSFER_DATE)
            , MOD_DT = SYSDATE()
        '''
        self.registrationFee_query = '''
        INSERT INTO REGISTRATION_FEE (
            REGISTRATION_DATE
            , START_ANNUAL
            , LAST_ANNUAL
            , PAYMENT_DEGREE
            , PAYMENT_FEE
            , PAYMENT_DATE
            , REGISTRATION_NUMBER
            , TRANSFER_DATE
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            START_ANNUAL = VALUES(START_ANNUAL)
            , LAST_ANNUAL = VALUES(LAST_ANNUAL)
            , PAYMENT_DEGREE = VALUES(PAYMENT_DEGREE)
            , PAYMENT_FEE = VALUES(PAYMENT_FEE)
            , PAYMENT_DATE = VALUES(PAYMENT_DATE)
            , TRANSFER_DATE = VALUES(TRANSFER_DATE)
            , MOD_DT = SYSDATE()
        ''' 
        self.match_info = {
            'right_info': [self.rightholder_info, self.conn_data],
            'reg_fee': [self.registrationFee_query, self.conn_data],
            'reg_rank': [self.rightRank_query, self.conn_data],
            'reg_rightA': [self.rightHolderA_query, self.conn_data],
            'reg_rightB': [self.rightHolderB_query, self.conn_data]
        }
        
    # params setting
    def get_searchtype(self):
        task_id_list=[]    
        tmp_app_list=[]
        for services in self.searchtype_services:
            target_url=f"{services.url}/{services.task_id}?transferDate={services.date}&searchType={services.searchType}&accessKey={services.key}"
            #1. 데이터를 가지고 오는 단계
            content_dict=self.item_check(target_url,low_level=True)
            sleep(1)
            #print(content_dict)
            print(content_dict['registrationTransferListInfo'].keys())
            print(len((content_dict['registrationTransferListInfo'].keys())))
            # 데이터 검증단계 
            transferCount='0'
            tmpList=[]
            
            if  len(content_dict.keys())!=1:
                transferCount=content_dict['transferCount']
                tmpList=content_dict['transferList']
            else:
                try:
                    transferCount=content_dict[f"{services.task_id}"]['transferCount']
                    tmpList=content_dict[f"{services.task_id}"]['transferList']
                    #print(transferCount)
                    #print(tmpList)
                except:
                    print('error')
                    
            if transferCount!=0:
                tmpList=tmpList.split('|')[:-1]
            else:
                print("no data here")
                
            if int(transferCount)!=len(tmpList):
                print("data transfer count incorrect")
            ############ 이 부분에서 Stage 1 종료. 변경사항이 있는 특허-실용 등록번호를 redis에 일시 저장한 뒤 하나씩 꺼내 진짜 데이터 추출에 활용############
            else:
                transferList=[number for number in tmpList if number.startswith('10')| number.startswith('20')]
                
                for number in transferList:
                    self.redis.sadd(f"{services.task_id}",number)
                    #print(number)
            
            if services.type == 'reg':
                task_id_list.append(services.task_id)
            union_transferList=self.redis.sunion(task_id_list)
            self.redis.delete(services.task_id)
            
            for number in union_transferList:
                self.redis.sadd(f'{services.type}_working',number)
                
                ##########이 부분 해결해야 함 ###################
                app_num=self.get_db(self.app_from_reg, self.conn_data_patent, number)
                
                if not len(app_num):
                    continue
                
                tmp_app_list.append(app_num[0][0])
                for app_num in tmp_app_list:
                   self.redis.sadd("app_working",app_num)

    def process_working(self, list_type, other=None,err_date=None):
        start = time.time()
        list_name= None
        # 오류 재실행 대비해 만들어 놓은 것.  -> 다른 방법이 없을까? 
        if other is None:
            list_name = f'{list_type}_working'
        else:
            list_name = other
        try:
            error_date = list(self.redis.smembers('work_date'))[0]
        except:
            error_date = datetime.datetime.now()-datetime.timedelta(1)
        
        if err_date is not None:
            error_date = err_date
        number_check = None
        while True:
            number = self.redis.spop(list_name) # key가 reg_working인 data를 하나씩 뽑아 씀. 
            if not number:
                break
            if number != number_check: # 당연히 같지 않다. 
                if list_type=='reg':
                    self.registration(number)
                    #self.registration(number, error_date)
            else:
                # 원래 이 부분에 출원정보 관련한 코드를 넣으려 했음. 
                print('something is wrong in working porocess..')
                continue
            duration = time.time() - start
            if duration < 0.5:
                time.sleep(0.5 - duration)
        self.post_many(flush=True)
    
    
    #http://plus.kipris.or.kr/openapi/rest/RegistrationService/registrationInfo?registrationNumber=2000642310000&accessKey=write your key
    
    
    # 등록사항 data input
    
    def registration(self,number):
        try:
            basic_url="http://plus.kipris.or.kr/openapi/rest/RegistrationService/"
            taskId="registrationInfo"
            reg_number='registrationNumber'
            #url =f'{basic_url}{taskId}?{reg_number}={number}&accessKey={api_key}'
            url =f'{basic_url}{taskId}?{reg_number}={number}&accessKey={self.api_key}'
            
            content=self.item_check(url)
            if len(content) !=0:
                for key,item in content.items():
                    if key=='regirtrationRightInfo':
                        if type(item) is not list:
                            item=[item]
                        else:
                            print('registraion_item_check process error')
                        for _item in item:
                            self.add_info(_item, only_none=True)              
        except:
            print('patent registration content input -> error')
        
    # insert ---
        try:
            
            
            rank_info=[]
            last_info=[]
            fee_info=[]
            
            right_info_=list(content['registrationRightInfo'])
            print(right_info_)
            right_idc_info=list(content['registrationRightInfo'].values())
            print(right_idc_info)
            right_a=[]
            right_b=[]
            
            
            if type(content['registrationLastRightHolderInfo']) is not list:
                last_info = list(content['registrationLastRightHolderInfo'].values())
            else:
                last_info= [list(orddict.values) for orddict in content['registrationLastRightHolderInfo']]
            if type(content['registrationRightRankInfo']) is not list:
                rank_info= list(content['registrationRightRankInfo'].values())
            else:
                rank_info = [list(orddict.values()) for orddict in content['registrationRightRankInfo']]
            if type(content['registrationFeeInfo']) is not list:
                fee_info=list(content['registrationFeeInfo'].values())
            else:
                fee_info=[list(orddict.values()) for orddict in content['registrationFeeInfo']]
            if type(content['registrationRightHolderInfo']['registrationRightHolderInfoA'] is not list):
                right_a=list(content['registrationRightHolderInfo']['registrationRightHolderInfoA'].values())
            else:
                right_a=[list(orddict.values()) for orddict in content['registrationRightHolderInfo']['registrationRightHolderInfoA']]
            if type(content['registrationRightHolderInfo']['registrationRightHolderInfoB']) is not list:
                right_b=list(content['registrationRightHolderInfo']['registrationRightHolderInfoB'])
            else:
                right_b=[list(orddict.values()) for orddict in content['registrationRightHolderInfo']['registrationRightHolderInfoB'].values()]
        except:
            print('something wrong in content_values')
            

    
    
    
     #----------------------------------------------------------------------
       #--------------------------- 사용 함수 ---------------------------------
       #----------------------------------------------------------------------                
       # mysql connection setting
       
    def get_db(self,conn_data,query,commit=False,retry=24):
        conn=pymysql.connect(host=conn_data['host'],
                             port=conn_data['port'],
                             user=conn_data['user'],
                             password=conn_data['password'],
                             database=conn_data['database'],
                             connect_timeout=60
                             )
        try:
            with conn.cursor() as curs:
                curs.execute(query)
                data = curs.fetchall()
                if commit:
                    conn.commit()
                conn.close()
                return data
        except:
            if tries==retry:
                conn.close()
            tries+=1
            sleep(5)
    def post_db(query, data, conn_data,retry=24,):
        tries= 0
        while True:
                
            try:
                conn=pymysql.connect(
                    host=conn_data['host'],
                    port=conn_data['port'],
                    user=conn_data['user'],
                    password=conn_data['password'],
                    database=conn_data['database'],
                    connect_timeout=60        
                    )
                with conn.cursor() as curs:
                    if (type(data[0]) is list) & (len(data) !=1):
                        curs.executemany(query, data)
                    elif (type(data[0]) is list) & (len(data) ==1):
                        curs.execute(query, data[0])
                    else:
                        curs.execute(query, data)
                conn.close()
                return True
            except:
                if tries==retry:
                    conn.close()
                    return False
                tries+1
                sleep(3)
                    
    def add_info(self,responses,number=None,only_none=False):
        if not only_none:
            responses['number'] = number
            responses['date'] = list(self.redis.smembers("work_date"))[0]
            
        for response in responses.items():
            if response[1]==None:
                if (response[0] == 'trialNumberr') | (response[0] == 'registrationNumber'):
                    responses[f'{response[0]}'] = 'N/A'
                responses[f'{response[0]}'] = ''

        




    # data information setting
    
    # data xml input 
    def item_check(self,url,low_level=False):
        try:
            request_get=requests.get(url)
            content_xml=request_get.content
            
            xd=xmltodict.parse(content_xml)
            xd_response=list(xd)[0]
            xd_res=xd[f'{xd_response}']
            xd_bd=list(xd_res)[0]
            xd_body=xd_res[f'{xd_bd}']
            xd_item=list(xd_body)[0]
            content=xd_body[f'{xd_item}']
            
            #key_name=list(xmltodict.parse(content_xml)['response']['body'])[0]
            #content=xmltodict.parse(content_xml)['response']['body'][f'{key_name}']
            
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
            print("item_check process error")


    # def post_manay(self, flush=False):
    #     if flush:
    #         for _key in sorted(self._many.keys()):
    #             try:
    #                 post_db()

    def post_db(self, query, data, conn_data,commit=True):
        tries=0
        while True:
            try:
                conn = pymysql.connect(host=conn_data['host'],
                                       port=conn_data['port'],
                                       user = conn_data['user'],
                                       password=conn_data['password'],
                                       database=conn_data['database'],
                                       connect_timeout=60)
                with conn.cursor() as curs:
                    if (type(data[0]) is list) & (len(data) !=1):
                        curs.executemany(query,data)
                    elif (type(data[0]) is list) & (len(data)==1):
                        curs.execute(query,data)
                if commit:
                    conn.commit()
                conn.close()
                return True
            except:
                if tries ==12:
                    conn.close()
                    return False
                tries +=1
                sleep(5)
    
    def post_many(self,flush=False):
        if flush:
            for _key in sorted(self._many.keys()):
                try:
                    self.post_db(self.match_info[_key][0], self._many[_key],self.match_info[_key][1])
                except:
                    print(_key)
                    print(self._many[_key])
                
if __name__ == '__main__':
    run = Kipris()
    #logging.debug('debug')
    #logging.info('info')
    print(run.process_working('reg'))
    #print(run.get_searchtype())
