import selenium as sel
import os
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

try:
    driver = sel.webdriver.Edge()
except:
    cwd = os.getcwd()
    path = os.path.join(cwd, 'msedgedriver.exe')
    driver = sel.webdriver.Edge(
        executable_path=r'Web_Scraping\Scripts\msedgedriver.exe')

driver.get('https://www.google.com/')
time.sleep(2)
