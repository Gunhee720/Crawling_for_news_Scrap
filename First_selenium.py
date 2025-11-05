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
url = "https://www.veritas-a.com/news/articleView.html?idxno=580632"
driver.get(url)

driver.execute_cdp_cmd("Page.printToPDF", {
    "path": "veritas_article.pdf",
    "printBackground": True
})

# query = driver.find_element(By.ID, "query")

# query.send_keys("뉴스")

# time.sleep(2)
# # search_btn = driver.find_element(By.ID,"search-btn")
# # search_btn.click()
# query.send_keys(Keys.ENTER)
# time.sleep(2)
# driver.save_screenshot("naver_news.png")

# driver.quit()