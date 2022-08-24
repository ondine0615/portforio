import selenium
import subprocess
import warnings
warnings.filterwarnings(action="ignore")

import requests
from selenium import webdriver
from pyvirtualdisplay import Display

display = Display(visible=0, size=(1920, 1080)) 
display.start() 

class Twtich(object):
    # VOD의 ID를 추출, 
    def extract_from_website(self):
                    
        path="/home/ondine0615/workplace/chat-log/chromedriver"
        driver = webdriver.Chrome(path)

        driver.get("https://www.twitchmetrics.net/c/49045679-woowakgood/videos?sort=published_at-desc")
        col=driver.find_element_by_class_name("col-9")
        _href=col.find_element_by_tag_name("a")
        _href_text=_href.get_attribute("href")
        _id=_href_text.split('/')[4]

        time=driver.find_element_by_class_name("time_ago")
        _date=time.get_attribute("datetime")
        broad_day=_date.split('T')[0]

        subprocess.run("/home/ondine0615/workplace/chat-log/data/TwitchDownloaderCLI -m ChatDownload --id {} --timestamp-format Relative -o {}.txt".format(_id,broad_day),shell=True)