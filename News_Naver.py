from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
url = "https://n.news.naver.com/article/001/0014999082"
driver.get(url)
time.sleep(2)

# 기사 제목
title = driver.find_element(By.CSS_SELECTOR, 'h2.media_end_head_headline').text

# 기사 본문
content = driver.find_element(By.CSS_SELECTOR, 'div#newsct_article').text

print("제목:", title)
print("본문:", content[:300], "...")  # 앞부분만 미리보기

driver.quit()
