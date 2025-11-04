from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# 브라우저 옵션
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

# PDF 저장을 위한 디렉토리
save_dir = "C:/news_pdfs"
os.makedirs(save_dir, exist_ok=True)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

query = "명지대"
url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query={query}"
driver.get(url)

# '옵션' 버튼 클릭
opt_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_option._search_option_open_btn")))
opt_btn.click()

# '1주' 버튼 클릭
week_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="txt" and text()="1주"]')))
week_btn.click()

time.sleep(2)

# 뉴스 기사 링크 모두 추출
links = [a.get_attribute("href") for a in driver.find_elements(By.CSS_SELECTOR, "a.news_tit")]

for i, link in enumerate(links[:5]):  # 예시로 5개만
    print(f"Saving article {i+1}: {link}")
    driver.get(link)
    time.sleep(3)

    # Chrome DevTools Protocol을 통해 PDF 저장
    pdf = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
    with open(os.path.join(save_dir, f"news_{i+1}.pdf"), "wb") as f:
        f.write(bytes(pdf['data'], encoding='base64'))
