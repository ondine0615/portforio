import pymysql
import requests
import xmltodict
import time
from datetime import datetime, timedelta
import os
import sys
import redis




class Kipris(object):
    def __init__(self, task_id=None):
        self.rd = redis.StrictRedis(host='192.168.0.13',port=6379, db=2)
        
        self.connect_mysql = {
            'host': '192.168.0.13',
            'port': 3306,
            'user': 'root',
            'database' : 'kipris',
        }
        self.api_key = "Y74vSqogy7fkw71F26g146N4s9Harc7sLqm4ONkWHWE="
        self.task_id = task_id
        self._many = {}
        
        
        self.url = 'http://plus.kipris.or.kr/openapi/rest/RegistrationService/'
        
        ###### 등록사항 api 정보 ###########
        # 0. 변동정보 -> 변동정보 operation를 통해 변동사항이 생긴 특허 등록번호를 받는다. 이 때 받은 번호가 권리정보, 권리자정보, 권리순위정보, 등록료정보, 
        self.list_services = [{
                'task_id' : "registrationInfo",
                'request_url':'http://plus.kipris.or.kr/openapi/rest/RegistrationService/',
                'params':['registrationNumber','accessKey'],
                'type_':'reg'
                }]
        self.lastRightHolder_delete_query = '''
                DELETE FROM LAST_RIGHT_HOLDER WHERE REGISTRATION_NUMBER IN (%s)
                '''
            

        
        
    def get_list(self, type_, date=None, just_check=False):
        list_service=self.list_services()
        redis_=self.rd()
        work_date=list(redis_.smembers("worK_date"))
        
        params={}
        
        for service_info in list_service:
            params[f"{service_info['key']}"] = self.api_key
            
            if date == None:
                params[f"{service_info['date']}"] = list(work_date)[0]
                
            else:
                params[f"{service_info['date']}"] = date
            
            # searchType이 필요한 경우 - > 등록사항에는 해당 안된다. 넘기자. 
            
            try:
                content_dict = self.check_data(service_info['url'],params, low_Level=True)
                time.sleep(0.1)
                
                transferCount ='0'
                tmpList = []
                
                # items 안에 더 있나 확인 후 count와 transferList 추출
                if len(content_dict.keys())!=1:
                    transferCount=content_dict['count']
                    tmpList=content_dict['transListString']
                else:
                    _task_id=service_info['task_id'].split('_')[0]
                    transferCount=content_dict[f'{_task_id}']['transferCount']
                    tmpList=content_dict[f'{_task_id}']['transferList']
                    
                #정상 케이스
                if transferCount != 0:
                    tmpList=tmpList.split('|')[:-1]
                    # count 검증
                    if int(transferCount) !=len(tmpList):
                        print('실제 들어온 데이터 개수가 맞지 않음')
                    target_date = params[f"{service_info['date']}"]
                    transferList = [number for number in tmpList if number.startswith('10') | number.startswith('20')]
                
                    if not just_check:
                        for number in transferList:
                            redis_.sadd(f"{service_info['task_id']}", number)
                else: # 당일 변경사항이 0이라면
                    print('변경사항이 없습니다.')
            except: # 에러 발생시
                print("변경사항 리스트 작업 중 에러가 발생")
    
    def data_union(self, type_):
        self.get_list(type_)
        
        task_id_list=[]
        
        for service_info in self.list_services:
            if service_info['type'] == type_:
                task_id_list.append(service_info['task_id'])
        union_transferList = self.rd.sunion(task_id_list)
        
        for task in self.list_services:
            if task['type'] ==type_:
                self.rd.delete(task['task_id']) # 중복사항을 제거하고 각각의 task_id는 모두 삭제한다. 
                
        for number in union_transferList:
            self.rd.sadd(f'{type_}_working', number)

    def data_working(self, list_type, api_key=None, other=None, err_date=None):
        redis_=self.rd()
        list_name = None
        if other is None:
            list_name = f'{list_type}_working'
        else:
            list_name = other
            
        error_date =list(redis_.smembers("work_date"))[0]
        
        if err_date is not None:
            error_date =err_date
            
        number_check = None
        
        while True:
            start = time.time()
            number = redis_.spop(list_name)
            if not number:
                break

            if number!=number_check:
                if list_type =='reg':
                    self.registration(number, error_date)
            duration=time.time() - start
            if duration < 0.5:
                time.sleep(0.5-duration)
        self.post_many(flush=True)
        
    

    def error_working(self, type_):
        strp_workdate = self.rd.smembers('work_date')
        today_datetime = datetime.strptime(list(strp_workdate)[0], '%Y%m%d')
        date_name_list = [f'{type_}_'+(today_datetime - timedelta(day)).strftime('%Y%m%d') + '_error' for day in range(1,8)]
        last_day = date_name_list[-1].split('_')[1]
        yesterday = date_name_list[0].split('_')[1]
        
        if type == 'reg':
            reg_past_list=self.rd.sunion(date_name_list)
            
        for date_name in date_name_list:
            self.working(type_, other=date_name, err_date=date_name.split('_')[1])
        
        check_day=(datetime.strptime(list(strp_workdate))[0], '%Y%m%d') - timedelta(8).strftime('%Y%m%d')
        check_list = self.rd.smembers(f'{type_}_{check_day}_error')
        self.rd.delete(f'{type_}_{check_day}_error')
        
    # 분류체계: 등록정보 / 오퍼레이션: 1. 등록사항 
    #https://plus.kipris.or.kr/portal/data/service/DBII_000000000000015/view.do?menuNo=210004&kppBCode=&kppMCode=&kppSCode=&subTab=&entYn=N&clasKeyword=#soap_ADI_0000000000009942
    def registration(self, number, error_date):
        try:
            basic_url = 'http://plus.kipris.or.kr/openapi/rest/RegistrationService/'
            operation_name = 'registrationInfo'
            basic_params = {
                'accessKey':self.api_key,
                'registrationNumber': number 
            }
            url = basic_url + operation_name
            content = self.check_data(url, basic_params)
            if len(content)!=0:
                for key, item in content.items():
                    if key == 'registrationRightInfo':
                        item['date'] = list(self.rd.smembers('work_date'))[0]
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
                        if type(item) is not list: item = [item]
                        for _item in item:
                            self.add_info(_item, number)
    
    
    
                #-------------------등록 정보 insert------------------
                _last_info = []
                _right_a = []
                _right_b = []
                _rank_info = []
                _fee_info = []
                #_right_info = list(content['registrationRightInfo'].values())
                _right_idc_info = list(content['registrationRightInfo'].values())
                del _right_idc_info[1]
                del _right_idc_info[7]
                del _right_idc_info[-1]
                if type(content['registrationLastRightHolderInfo']) is list:
                    _last_info = [list(info_.values()) for info_ in content['registrationLastRightHolderInfo']]
                else:_last_info = list(content['registrationLastRightHolderInfo'].values()) # 권리자 정보
                if type(content['registrationRightHolderInfo']['registrationRightHolderInfoA']) is list:   
                    _right_a = [list(info_.values()) for info_ in content['registrationRightHolderInfo'] ['registrationRightHolderInfoA']]  # 권리자 정보A
                else: 
                    _right_a = list(content['registrationRightHolderInfo']['registrationRightHolderInfoA'].values())
                if type(content['registrationRightHolderInfo']['registrationRightHolderInfoB']) is list:
                    _right_b = [list(info_.values()) for info_ in content['registrationRightHolderInfo']['registrationRightHolderInfoB']] # 권리자정보B
                else: _right_b = list(content['registrationRightHolderInfo']['registrationRightHolderInfoB'].values())
                if type(content['registrationRightRankInfo']) is list:
                    _rank_info = [list(info_.values()) for info_ in content['registrationRightRankInfo']] # 권리순위정보
                else: 
                    _rank_info = list(content['registrationRightRankInfo'].values())
                if type(content['registrationFeeInfo']) is list:
                    _fee_info = [list(info_.values()) for info_ in content['registrationFeeInfo']]
                else: 
                    _fee_info = list(content['registrationFeeInfo'].values())

                self.post_data('reg_right_a', _right_a)
                
                self.post_data('reg_right_b', _right_b)

                self.post_data('reg_rank', _rank_info)
                
                self.post_data('reg_fee', _fee_info)
                
                self.post_db(self.lastRightHolder_delete_query, number, self.conn_data)
                
                self.post_data('reg_last', _last_info)
                
                self.post_data('reg_idc', _right_idc_info)
                
                self.post_data('reg_update', [number, list(self.rd.smembers('work_date_dash'))[0]])

        except:
            print("등록정보 insert 중 에러 발생")
    
    
    
    
    
    
    
    
    def check_data(self, url, params, low_level=False):
        
        res = requests.get(url=url, params=params)
        content_xml=res.content
        key_name=list(xmltodict.parse(content_xml)['response']['body'][0])
        content=xmltodict.parse(content_xml)['response']['body'][f'{key_name}']
        
        if content is None:
            return []
        else:
            if low_level:
                return content
            detail_name=list(content)[0]
            content =content[detail_name]
            return content
    
        
    def add_info(self, info_, number=None):
        info_['number'] =number
        info_['data'] = list(self.rd.smembers('work_date'))[0]
        
        for inf in info_.items():
            if inf[1] ==None:
                if (inf[0] == 'trialNumber') | (inf[0]=='registrationNumber'):
                    info_[f'{info_[0]}'] = 'N/A'
                info_[f'{info_[0]}'] =''
            
            
    
    def post_data(self, target=None, data=None, flush=False):

        if isinstance(data, (list, tuple)):
            if isinstance(data[0], (list, tuple)):
                self._many[target] = data
            else:
                self._many[target] = [data]
                
        else:
            self._many[target] == [[data]]
            
        if isinstance(data, (list, tuple)):
            if isinstance(data[0], (list,tuple)):
                self._many[target].extend(data)
            else:
                self._many[target].append([data])
        if len(self._many[target]) ==100:
            self.post_db(self.match_info[target[0]])
                    
        
    def post_db(self, query, data, connect_mysql, connect_timeout=60, retry=12, retry_interval=5, commit=True):
        
        try:
            conn = pymysql.connect(host=connect_mysql['host'],
                                   port=connect_mysql['port'],
                                   user=connect_mysql['user'],
                                   database=connect_mysql['database'],
                                   connect_timeout=connect_timeout)
            
            with conn.cursor() as curs:
                if (type(data[0]) is list) & (len(data) !=1):
                    curs.executemany(query, data)
                elif (type(data[0]) is list) & (len(data) ==1):
                    curs.execute(query, data[0])
                else:
                    curs.execute(query, data)
                    
            if commit:
                conn.commit()
            conn.close()
            
            return True
        except:
            if tries==retry:
                conn.close()
                return False
        tries +=1
        time.sleep(retry_interval)
        
        
        
    
    
    
    def get_db(query, connect_mysql, param=None, connect_timeout=60, retry=24, retry_interval=5,commit=False):
        
        try:
            conn = pymysql.connect(host=connect_mysql['host'],
                                   port=connect_mysql['port'],
                                   user=connect_mysql['user'],
                                   password=connect_mysql['password'],
                                   database=connect_mysql['database'],
                                   connect_timeout=connect_timeout)
            with conn.cursor() as curs:
                if param in None:
                    curs.execute(query)
                else:
                    curs.execute(query, param)
                data = curs.fetchall()
                if commit:
                    conn.commit()
                conn.close()
                return data
        except:
            if tries==retry:
                conn.close()
            tries+=1
            time.sleep(retry_interval)
            
    
    