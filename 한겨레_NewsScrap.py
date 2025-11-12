from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time, base64, os, random

# ====== 기본 설정 ======
query = "명지대"
today = datetime.now().strftime("%Y%m%d")
save_dir = f"./NewsPDFs/{query}_한겨례_{today}/"
os.makedirs(save_dir, exist_ok=True)

# ====== 브라우저 설정 ======
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# ====== 검색 페이지 접속 ======
url = "https://search.hani.co.kr/search?searchword=%EB%AA%85%EC%A7%80%EB%8C%80&sort=desc&startdate=&enddate=&dt=searchPeriod"
driver.get(url)
time.sleep(3)

# ====== 검색 옵션 클릭 ======
opt_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.search-filter-list > div.search-filter-item.dropdown-list-wrap:nth-of-type(2) button.selected.search-selected")))
opt_btn.click()
print("✅ 검색 옵션 버튼 클릭 완료")
time.sleep(1.5)

# ====== 1주 옵션 클릭 및 확인 ======
confirm_btn = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='period_3']"))
)
confirm_btn.click()
print("✅ 1주 옵션 적용 완료")



# ====== 기사 리스트 로딩 대기 ======
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.article-list li article")))
print("✅ 기사 목록 로딩 완료")

# ====== 기사 블록 탐색 ======
cards = driver.find_elements(By.CSS_SELECTOR, "div.search-result-section ul.article-list li article a.flex-inner[href]")
print(f"📰 총 {len(cards)}개의 기사 감지됨")

visited = set()
count = 0

for card in cards:
    try:
        href = card.get_attribute("href")
        if not href or not href.startswith("http") or href in visited:
            continue
        visited.add(href)
        count += 1

        print(f"\n[{count}] {href} 저장 시도 중...")

        # 새 탭으로 열기
        driver.execute_script(f"window.open('{href}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        # 기사 로딩 대기
        time.sleep(random.uniform(4, 6))

        # 파일 이름 생성
        title = driver.title.strip()
        safe_title = (
            title.replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace("*", "_")
            .replace("?", "_")
            .replace("\"", "_")
            .replace("<", "_")
            .replace(">", "_")
            .replace("|", "_")
        )

        filename = os.path.join(save_dir, f"{count:02d}_{safe_title[:40]}.pdf")

        if os.path.exists(filename):
            print(f"⚠️ 이미 존재: {filename}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

        # ✅ PDF 저장
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "landscape": False,
            "scale": 1
        })
        pdf_bytes = base64.b64decode(pdf_data['data'])

        with open(filename, "wb") as f:
            f.write(pdf_bytes)

        print(f"✅ 저장 완료: {filename}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        time.sleep(random.uniform(3, 6))

    except Exception as e:
        print(f"⚠️ 오류 발생: {e}")
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        continue

print(f"\n🎉 모든 기사 PDF 저장 완료! ({count}개)")
print(f"📁 저장 경로: {os.path.abspath(save_dir)}")
driver.quit()