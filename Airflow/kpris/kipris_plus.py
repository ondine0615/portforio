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
        self.api_key_ = "Y74vSqogy7fkw71F26g146N4s9Harc7sLqm4ONkWHWE="
        self.api_key = "S5sUeUcewvE0=dLF=a9IKgK72zEAvD5bkiPciv4BIEU="
        #mysql_reg_database(등록번호 기반)
        self.conn_data = {
            'host' : '127.0.0.1',
            'port' : 3306,
            'user': 'root',
            'password':'123',
            'database': "KIPRIS"
        }
        # mysql_patent_database(출원번호 기반; 예정)
        self.conn_data_patent= None
        {
            'host':'127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '123',
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
            RANK_CORRELATOR_ADDRESS= VALUES(RANK_CORRELATOR_ADDRESS),
            TRANSFER_DATE=VALUES(TRANSFER_DATE)      
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
            INDECATION_OF_EVENT = VALUES(INDECATION_OF_EVENT),
            TRANSFER_DATE = VALUES(TRANSFER_DATE)
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
    
        '''
        self.registrationFee_query = '''
        INSERT INTO REGISTRATION_FEE (
            REGISTRATION_DATE
            , START_ANNUAL
            , LAST_ANNUAL
            , ENT_DEGREE
            , PAYMENT_FEE
            , PAYMENT_DATE
            , REGISTRATION_NUMBER
            , TRANSFER_DATE
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            START_ANNUAL = VALUES(START_ANNUAL)
            , LAST_ANNUAL = VALUES(LAST_ANNUAL)
            , ENT_DEGREE = VALUES(ENT_DEGREE)
            , PAYMENT_FEE = VALUES(PAYMENT_FEE)
            , PAYMENT_DATE = VALUES(PAYMENT_DATE)
            , TRANSFER_DATE = VALUES(TRANSFER_DATE)
    
        ''' 
        self.lastRightHolder_insert_query = '''
        INSERT INTO LAST_RIGHT_HOLDER (
            LAST_RIGHT_HOLDER_NUMBER
            , LAST_RIGHT_HOLDER_NAME
            , LAST_RIGHT_HOLDER_ADDRESS
            , LAST_RIGHT_HOLDER_COUNTRY
            , REGISTRATION_NUMBER
            , TRANSFER_DATE
        ) VALUES (%s,%s,%s,%s,%s,%s)
        '''
        self.lastRightHolder_delete_query = '''
        DELETE FROM LAST_RIGHT_HOLDER WHERE REGISTRATION_NUMBER IN (%s)
        '''
        self.registration_idc_query = '''
        INSERT INTO KIPO_ADMIN_REG_BS (
            registerNumber
            , registerationDate
            , examinationDate
            , existDuringDate
            , lapsCause
            , lapsDate
            , applicationNumber
            , applicationDate
            , publicationNumber
            , publicationDate
            , internationRegistrationNumber
            , internationRegistrationDate
            , originalApplicationNumber
            , originalApplicationDate
            , classificationCode
            , inventionTitle
            , inventionTitleEng
            , claimCount
            , priorityCountry
            , priorityDate
            , priorityCount
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                ,%s)
        ON DUPLICATE KEY UPDATE
            inventionTitle = VALUES(inventionTitle)
            , inventionTitleEng = VALUES(inventionTitleEng)
            , registerationDate = VALUES(registerationDate)
            , lapsCause = VALUES(lapsCause)
            , lapsDate = VALUES(lapsDate)
            , applicationNumber = VALUES(applicationNumber)
            , applicationDate = VALUES(applicationDate)
            , publicationNumber = VALUES(publicationNumber)
            , publicationDate = VALUES(publicationDate)
            , classificationCode = VALUES(classificationCode)
            , examinationDate = VALUES(examinationDate)
            , existDuringDate = VALUES(existDuringDate)
            , claimCount = VALUES(claimCount)
            , originalApplicationNumber = VALUES(originalApplicationNumber)
            , originalApplicationDate = VALUES(originalApplicationDate)
            , priorityCount = VALUES(priorityCount)
            , priorityCountry = VALUES(priorityCountry)
            , priorityDate = VALUES(priorityDate)
            , internationRegistrationNumber = VALUES(internationRegistrationNumber)
            , internationRegistrationDate = VALUES(internationRegistrationDate)
            '''
        self.registration_update = '''
            INSERT INTO REG_UPDATE_HISTORY (
            registration_number
            , REGISTRATION
            ) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            REGISTRATION = VALUES(REGISTRATION)
        '''






        self.match_info = {
            'right_info': [self.rightholder_info, self.conn_data],
            'reg_fee': [self.registrationFee_query, self.conn_data],
            'reg_rank': [self.rightRank_query, self.conn_data],
            'reg_right_a': [self.rightHolderA_query, self.conn_data],
            'reg_right_b': [self.rightHolderB_query, self.conn_data],
            'reg_last': [self.lastRightHolder_insert_query, self.conn_data],
            'reg_idc': [self.registration_idc_query, self.conn_data],
            'reg_update': [self.registration_update, self.conn_data],
        }
        
    # params setting
    def get_searchtype(self):
        task_id_list=[]    
        tmp_app_list=[]
        for services in self.searchtype_services:
            target_url=f"{services.url}/{services.task_id}?transferDate={services.date}&searchType={services.searchType}&accessKey={services.key}"

            #1. 데이터를 가지고 오는 단계
            content_dict=self.item_check(target_url)
            sleep(1)
            #print(content_dict)
            #print(content_dict['registrationTransferListInfo'])
            #print(len((content_dict['registrationTransferListInfo'].keys())))
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
                # app_num=self.get_db(self.app_from_reg, self.conn_data_patent, number)
                
                # if not len(app_num):
                #     continue
                
                # tmp_app_list.append(app_num[0][0])
                # for app_num in tmp_app_list:
                #    self.redis.sadd("app_working",app_num)

    def process_working(self, list_type):
        start = time.time()
        list_name= f'{list_type}_working'
        
        number_check = None
        while True:
            number = self.redis.spop(list_name) # key가 reg_working인 data를 하나씩 뽑아 씀. 
            #if not number:
            #    break
            if number != number_check: # 당연히 같지 않다. 
                if list_type=='reg':
                    self.registration(number)
                    number_check=number # 중복을 방지하기 위해
            else:
                pass
            #else:
                # 원래 이 부분에 출원정보 관련한 코드를 넣으려 했음. 
            #    print('something is wrong in working porocess..')
            #py    continue
            duration = time.time() - start
            if duration < 0.5:
                time.sleep(0.5 - duration)
            self.post_many(flush=True)
            #self.post_many(flush=True)
            print('process working complete')
    
    
    # 등록사항 data input
    
    def registration(self,number):
        
        #try:
        basic_url="http://plus.kipris.or.kr/openapi/rest/RegistrationService/"
        taskId="registrationInfo"
        reg_number='registrationNumber'
        #url =f'{basic_url}{taskId}?{reg_number}={number}&accessKey={api_key}'
        url =f'{basic_url}{taskId}?{reg_number}={number}&accessKey={self.api_key}'

        content=self.item_check(url)
        if len(content) !=0:
            for key,item in content.items():
                if key=='registrationRightInfo':
                    item['date'] = list(self.redis.smembers('work_date'))[0]
                    self.add_info(item, only_none=True)
                elif key == 'registrationRightHolderInfo':
                    if type(item['registrationRightHolderInfoA']) is list:
                        for _item in item['registrationRightHolderInfoA']:
                            self.add_info(_item, number)
                    else:
                        self.add_info(item['registrationRightHolderInfoA'], number)
                    if type(item['registrationRightHolderInfoB']) is list:
                        for _item in item['registrationRightHolderInfoB']:
                            self.add_info(_item, number)
                    else:
                        self.add_info(item['registrationRightHolderInfoB'], number)
                else:
                    if type(item) is not list:
                        item = [item]
                    for _item in item:
                        self.add_info(_item, number)
        #except Exception as e:
            #print('patent registration content input -->',e)
    # insert ---
        #try:
            
            
        rank_info=[]
        _last_info=[]
        fee_info=[]
        right_a=[]
        right_b=[]


        #right_info_=list(content['registrationRightInfo'])
        #print(right_info_)
        right_idc_info=list(content['registrationRightInfo'].values())
        print(right_idc_info)
        
        del right_idc_info[1]
        del right_idc_info[7]
        del right_idc_info[-1]
        
        
        if type(content['registrationLastRightHolderInfo']) is not list:
            _last_info = list(content['registrationLastRightHolderInfo'].values())
        else:
            _last_info= [list(data.values()) for data in content['registrationLastRightHolderInfo']]
        
        if type(content['registrationRightRankInfo']) is not list:
            rank_info= list(content['registrationRightRankInfo'].values())
        else:
            rank_info = [list(data.values()) for data in content['registrationRightRankInfo']]
        
        if type(content['registrationFeeInfo']) is not list:
            fee_info=list(content['registrationFeeInfo'].values())
        else:
            fee_info=[list(data.values()) for data in content['registrationFeeInfo']]

        if type(content['registrationRightHolderInfo']['registrationRightHolderInfoA']) is list:
            right_a = [list(data.values()) for data in content['registrationRightHolderInfo']['registrationRightHolderInfoA']]            
        else:
            right_a=list(content['registrationRightHolderInfo']['registrationRightHolderInfoA'].values())
        #right_a=list(content['registrationRightHolderInfo']['registrationRightHolderInfoA'].values())

        if type(content['registrationRightHolderInfo']['registrationRightHolderInfoB']) is list:
            right_b = [list(data.values()) for data in content['registrationRightHolderInfo']['registrationRightHolderInfoB']]
        else:
            right_b = list(content['registrationRightHolderInfo']['registrationRightHolderInfoB'].values())
             
        
        self.post_many('reg_right_a',right_a) # target, data
        self.post_many('reg_right_b',right_b)
        self.post_many('reg_rank',rank_info)
        self.post_many('reg_fee',fee_info)
        self.post_db(self.lastRightHolder_delete_query, number)
        self.post_many('reg_last',_last_info)
        self.post_many('reg_idc',right_idc_info)
        self.post_many('reg_update',[number, list(self.redis.smembers('work_date'))[0]])
        print("complete")
        # except ValueError:
        #     print('something wrong in content_values')
            

    
    
    
     #----------------------------------------------------------------------
       #--------------------------- 사용 함수 ---------------------------------
       #----------------------------------------------------------------------                
       # mysql connection setting
       
    def get_db(self,query,commit=False,retry=24):
        tries=0
        conn=pymysql.connect(host=self.conn_data['host'],
                             port=self.conn_data['port'],
                             user=self.conn_data['user'],
                             password=self.conn_data['password'],
                             database=self.conn_data['database'],
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
    def add_info(self,orddict,number=None,only_none=False):
        if not only_none:
            orddict['number'] = number
            orddict['date'] = list(self.redis.smembers("work_date"))[0]
            
        for response in orddict.items():
            if response[1]==None:
                if (response[0] == 'trialNumberr') | (response[0] == 'registrationNumber'):
                    orddict[f'{response[0]}'] = 'N/A'
                orddict[f'{response[0]}'] = ''

        




    # data information setting
    
    # data xml input 
    def code_check(self, url):
        try:
            request_get=requests.get(url)
            content_xml=request_get.content
            body=list(xmltodict.parse(content_xml)['response']['body'])[0]
            content=xmltodict.parse(content_xml)['response']['body'][f'{body}']
            
            return content

            
        except:
            print(' error in api_code check process')
    
    def item_check(self,url):
        
        try:
            request_get=requests.get(url)
            content_xml=request_get.content
            body=list(xmltodict.parse(content_xml)['response']['body'])[0]
            content=xmltodict.parse(content_xml)['response']['body'][f'{body}']
            detail_name=list(content)[0]
            content=content[detail_name]
            return content
        except:
            print("item_check process error")


    # def post_manay(self, flush=False):
    #     if flush:
    #         for _key in sorted(self._many.keys()):
    #             try:
    #                 post_db()

    def post_db(self, query, data):
        tries=0
        print('post_db 함수 진입')
        while True:
            #try:
            conn = pymysql.connect(host=self.conn_data['host'],
                                    port=self.conn_data['port'],
                                    user = self.conn_data['user'],
                                    password=self.conn_data['password'],
                                    database=self.conn_data['database'],
                                    connect_timeout=60)
            with conn.cursor() as curs:
                if (type(data[0]) is list) & (len(data) !=1):
                    curs.executemany(query,data)
                elif (type(data[0]) is list) & (len(data)==1):
                    curs.execute(query,data)
            #if commit:
            conn.commit()
            print('commit 완료')
            conn.close()
            sleep(3)
            return True
            # except:
            #     if tries ==2:
            #         conn.close()
            #         return False
            #     tries +=1
            




    def post_many(self, target=None, data=None, flush=False):
        if not flush:
            if target not in self._many.keys():
                if isinstance(data, (list, tuple)):
                    if isinstance(data[0], (list, tuple)):
                        self._many[target] = data
                    else:
                        self._many[target] = [data]
                else:
                    self._many[target] = [[data]]
            else:
                if isinstance(data, (list, tuple)):
                    if isinstance(data[0], (list, tuple)):
                        self._many[target].extend(data)
                    else:
                        self._many[target].append(data)
                else:
                    self._many[target].append([data])
            if len(self._many[target]) == 2:
                self.post_db(self.match_info[target][0], self._many[target])
                self._many.pop(target)
        if flush:
            for _key in sorted(self._many.keys()):
                try:
                    self.post_db(self.match_info[_key][0], self._many[_key])
                except:
                    print(_key)
                    print(self._many[_key])
 
 
 
 
    # def post_many(self,flush=False,target=None,data=None):
    #     if flush:
    #         for _key in sorted(self._many.keys()):
    #             try:
    #                 self.post_db(self.match_info[_key][0], self._many[_key], self.match_info[_key][1])
    #             except:
    #                 print(_key)
    #                 print(self._many[_key])
    #     if not flush:
    #         if target not in self._many.keys():
    #             if isinstance(data, (list,tuple)):
    #                 if isinstance(data[0], (list,tuple)):
    #                     self._many[target]=data
    #                 else:
    #                     self._many[target]=[data]
    #                     #print('post_many processing error')
    #             else:
    #                 self._many[target]=[[data]]
    #                 #print('post_many data type error')
    #         else:
    #             print('post_many target processing error')
    #     if len(self._many[target]) ==5:
    #         self.post_db(self.match_info[target][0], self._many[target],self.match_info[target][1])
    #         self._many.pop(target)
    #         print('db insert complete, delete info...')
    #     else:
    #         print('aldsfkjsld')
    
        # if flush:
        #     for _key in sorted(self._many.keys()):
        #         try:
        #             self.post_db(self.match_info[_key][0], self._many[_key],self.match_info[_key][1])
        #         except:
        #             print(_key)
        #             print(self._many[_key])
                
if __name__ == '__main__':
    run = Kipris()
    #logging.debug('debug')
    #logging.info('info')
    #print(run.get_searchtype())
    #run.get_searchtype()
    run.process_working('reg')
    #print(run.process_working('reg'))
    #print(run.get_searchtype())
