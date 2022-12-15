import unittest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver=webdriver.Chrome('./chromedriver',options=chrome_options)        
    def test_login(self):
        wait=WebDriverWait(self.driver,10)
        self.driver.get(url)
        self.driver.find_element_by_id('txtUsernmae').send_keys('ondine0615')
        self.driver.find_element_by_id('txtPassword').send_keys('guswlsrbaks35'+Keys.RETURN)
        try:
            wait.until(EC.element_to_be_clickable((By.CLASS,"ProductPrice")))
        except:
            print("a")
        b=self.driver.find_element_by_class_name('ProductPrice').text
        return b
lt=LoginTest()
print(lt.test_login())