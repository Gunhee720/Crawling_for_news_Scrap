from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support import expected_conditions as EC
#옵션
options = Options()
options.add_argument("--start-maximized")  # 브라우저 최대화 (선택)
options.add_experimental_option("detach",True)  

#

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 4)
url = "https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query=%EB%AA%85%EC%A7%80%EB%8C%80"
driver.get(url)

news_option_btn = driver.find_element(By.CSS_SELECTOR,".btn_option _search_option_open_btn")
news_option_btn.click()

# query = driver.find_element(By.ID, "query")

# query.send_keys("뉴스")

# time.sleep(2)
# # search_btn = driver.find_element(By.ID,"search-btn")
# # search_btn.click()
# query.send_keys(Keys.ENTER)
# time.sleep(2)
# driver.save_screenshot("naver_news.png")

# driver.quit()