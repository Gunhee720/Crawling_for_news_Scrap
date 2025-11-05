import base64
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === 브라우저 설정 ===
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# === 저장 경로 ===
save_dir = r"C:Users/USER/OneDrive/Desktop/news_pdfs"
os.makedirs(save_dir, exist_ok=True)

query = "명지대"
url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query={query}"
driver.get(url)

# === 검색 옵션 설정 ===
opt_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_option._search_option_open_btn")))
opt_btn.click()

week_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="txt" and text()="1주"]')))
week_btn.click()
time.sleep(2)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3)")
time.sleep(2)

# === 기사 링크 수집 ===
news_links = driver.find_elements(
    By.CSS_SELECTOR,
    "div.sds-comps-vertical-layout.sds-comps-full-layout[data-template-type='vertical'] a[href]"
)

hrefs = []
for link in news_links:
    href = link.get_attribute("href")
    if href and href.startswith("http") and href not in hrefs:
        hrefs.append(href)

print(f"총 {len(hrefs)}개의 뉴스 링크 발견")

# === 기사 방문 + PDF 저장 ===
for idx, href in enumerate(hrefs, 1):
    try:
        print(f"\n[{idx}] 방문 중: {href}")
        driver.execute_script(f"window.open('{href}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        # === PDF 저장 (핵심 부분) ===
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
        pdf_bytes = base64.b64decode(pdf_data["data"])

        # 파일명 생성
        safe_title = driver.title.replace("/", "_").replace("\\", "_").strip()[:100]
        pdf_path = os.path.join(save_dir, f"{idx:02d}_{safe_title}.pdf")

        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"🧾 PDF 저장 완료 → {pdf_path}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)

    except Exception as e:
        print(f"⚠️ 오류 발생: {e}")
        driver.switch_to.window(driver.window_handles[0])

print("\n✅ 모든 기사 PDF 저장 완료!")
