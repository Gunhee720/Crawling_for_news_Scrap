from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

# 드라이버 실행
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

url = "https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query=명지대"
driver.get(url)

# 옵션 버튼 클릭
news_option_btn = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_option._search_option_open_btn"))
)
news_option_btn.click()


# '1주' 버튼 클릭
week_btn = wait.until(
    EC.element_to_be_clickable((By.XPATH, '//a[@class="txt" and text()="1주"]'))
)
week_btn.click()


# ✅ 첫 번째 헤드라인 기사
head1 = driver.find_element(By.CSS_SELECTOR,".sds-comps-text.sds-comps-text-ellipsis.sds-comps-text-ellipsis-1.sds-comps-text-type-headline1") 
print("✅ 첫 번째 헤드라인 뉴스:", head1.text)
head1.click()

time.sleep(2)
driver.close()
# ✅ 헤드라인 기사들 중 두 번째 기사
head1_2 = driver.find_elements(By.CSS_SELECTOR, '.sds-comps-text.sds-comps-text-ellipsis.sds-comps-text-ellipsis-1.sds-comps-text-type-body2.toxDoSrhtPXfHrN5nwx2')
head1_2.click()
time.sleep(3)
driver.close()



