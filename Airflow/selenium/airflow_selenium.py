from airflow import DAG
from airflow.providers.sqlite.operators.sqlite import SqliteOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import chromedriver_autoinstaller

from pandas import json_normalize
import pandas as pd

from datetime import datetime
import datetime


from email.policy import default
import imp
import math




def _pulling_data(yesterday):    
    display = Display(visible=0, size=(1920, 1080)) 
    display.start() 
    
    chromedriver_autoinstaller.install()   
    #path='/home/ondine0615/airflow/dag/chromedriver' 
    browser = webdriver.Chrome()
    
    today = datetime.date.today()
    yesday=today-datetime.timedelta(1)
    yesterday= str(yesday.strftime('%Y.%m.%d'))
    
    #airflow/dag/chromedriver
    # 웹 자원을 로드하기위해 3초까지 기다려 준다
    browser.implicitly_wait(3)
    # url 접근
    browser.get('https://www.kisrating.co.kr/ratingsStatistics/statics_spread.do')
    # 기준일 설정
    search_box = browser.find_element(By.NAME,"startDt")
    #search_box = browser.find_element_by_name("startDt")
    search_box.clear()  # 입력하기전 Text 초기화 하기
    search_box.send_keys(yesterday)  # 시간 값
    search_box.submit()  # 시간 값 입력
    browser.find_element(By.ID,"btnSearch").click()
    #browser.find_element_by_id("btnSearch").click()  # 검색

    # 페이지 html 가져오기
    html = browser.page_source
    # Beautifulsoup을 사용하기 위해 soup에 데이터 넣기
    soup = BeautifulSoup(html, 'html.parser')

    # 새롭게 검색한 웹 페이지에서 데이터 파싱
    """ 
    #Selenium으로 파싱
    search_table = browser.find_element_by_class_name("table_ty1")
    print(search_table.text)
    """
    # BeautifulSoup 으로 파싱 => search_table[0] = interest rate of BBB-
    search_table = soup.select("table:nth-of-type(1) tr:nth-of-type(11) td:nth-of-type(9)")
    #print(search_table[0].text)
    BBBm = float(search_table[0].text)

    # 팝업 창 닫기
    browser.close()

    # today = datetime.date.today()
    # yesterday=today-datetime.timedelta(1)
    # BBBm = interest_rate(str(yesterday.strftime('%Y.%m.%d')))
    
    
    url_templ = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A%s&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=701"
    url = url_templ % ('007070')

    # User setting ROE value
    setting = 1  # 0 = 재무제표의 ROE, 1 = 사용자가 정한 ROE
    set_ROE = 8.14  # 사용자가 정한 ROE

    # 네이버 금융에서 크롤링할 경우
    # tables = pd.read_html(url, encoding='euc-kr')
    tables = pd.read_html(url)

    # 현재 주가
    df_present = tables[0]
    present = int(str(df_present.loc[0, 1]).replace(',', '').split('/')[0])

    # 발행주식수 (보통주/우선주)
    df_issued_stock = tables[0]  # print(tables[0])
    issued_stock = df_issued_stock.loc[df_issued_stock[0] == '발행주식수(보통주/ 우선주)', 1]
    issued_stock = str(df_issued_stock.loc[6, 1]).replace(',', '').split('/')
    common_stock = int(issued_stock[0])  # 보통주
    preferred_stock = int(issued_stock[1])  # 우선주

    # 자기주식
    df_treasury_stock = tables[4]
    self_stock = df_treasury_stock.loc[df_treasury_stock['주주구분'] == '자기주식 (자사주+자사주신탁)', '보통주']
    if math.isnan(self_stock):  # 자기주식을 가지고 있지 않을 경우
        treasury_stock = 0

    else:  # 자기주식을 가지고 있을 경우
        treasury_stock = int(self_stock)

    number_of_stock = common_stock - preferred_stock - treasury_stock

    # 자본
    df_capital = tables[10]
    capital = int(df_capital.loc[9][3] * 100000000)

    # ROE
    ROE = df_capital.loc[17]
    roe_first = ROE[1]
    roe_second = ROE[2]
    roe_third = ROE[3]
    if roe_first > roe_second > roe_third:
        rep_ROE = roe_third
    elif roe_first < roe_second < roe_third:
        rep_ROE = roe_third
    else:
        rep_ROE = (roe_first + roe_second + roe_third) / 3

    #
    if setting == 1:
        rep_ROE = set_ROE

    # 기업 가치 (=Enterprise value(EV))
    excess_earnings = capital * (rep_ROE - BBBm) / 100
    EV = int(capital + (capital * (rep_ROE - BBBm)) / BBBm)
    EV_10 = int(capital + (excess_earnings * 0.9 / (1 - 0.9 + (BBBm / 100))))
    EV_20 = int(capital + (excess_earnings * 0.8 / (1 - 0.8 + (BBBm / 100))))

    # 적정 주가 구하기
    stock_ideal = int(EV / number_of_stock)
    stock_10 = int(EV_10 / number_of_stock)
    stock_20 = int(EV_20 / number_of_stock)

    processed_save=json_normalize(
        {"number_of_stock": stock['number_of_stock'],
        'capital': stock['capital'],
        'ROE': stock['ROE'],
        'EV': stock['EV'],
        'present': stock['present'],    
        'stock_ideal': stock['stock_ideal'],
        'stock_10': stock['stock_10'],
        'stock_20': stock['stock_20']})
    
#--------------------------------

default_args = {
  'start_date': datetime.datetime(2022, 1, 1),
}


with DAG(
    dag_id='stock_pipeline',
    schedule_interval='@daily',
    default_args=default_args,
    tags=['stock'],
    catchup=False) as dag:  
    
    creating_table=SqliteOperator(
        task_id='creating_table',
        sqlite_conn_id='db_sqlite',
        sql="""
            CREATE TABLE IF NOT EXISTS stock (
                number_of_stock int,
                capital int,
                ROE int,
                present int,
                stock_ideal int,
                stock_10 int,
                stock_20 int
            )
        """
    )

    process_scraping=PythonOperator(
        task_id='process_scraping',
        python_callable=_pulling_data
    )
    
    save_data=BashOperator(
        task_id="save_data",
        bash_command='echo -e ".separator ","\n.import /tmp/save_data.csv users" | sqlite3 /home/ondine0615/airflow/airflow.db'
    )
    
    creating_table >> process_scraping >> save_data
