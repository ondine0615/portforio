from time import sleep
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
from selenium.webdriver.support import expected_conditions as EC
url='https://cafe.naver.com/joonggonara?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D10050146%2526page%3D1%2526menuid%3D334%2526boardtype%3DL%2526articleid%3D957821437%2526referrerAllArticles%3Dfalse'

def find_price(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')    
    driver = webdriver.Chrome(executable_path='./chromedriver',options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(3)
    p_tag = WebDriverWait(driver,timeout=20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="cafe_main"]')))
    driver.switch_to.frame(p_tag)
    sleep(5)
    src=driver.page_source
    sleep(5)
    soup=bs(src,'html.parser')

    return soup.find('div',class_='ProductPrice').text