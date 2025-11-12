from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time, base64, os, random

#alert handling imports
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoAlertPresentException,
    StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.common.alert import Alert
# ====== 기본 설정 ======
query = "명지대"
today = datetime.now().strftime("%Y%m%d")
save_dir = f"./NewsPDFs/{query}_조선일보_{today}/"
os.makedirs(save_dir, exist_ok=True)

# ====== 브라우저 설정 ======
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# ====== 검색 페이지 접속 ======
url = (
    "https://www.chosun.com/nsearch/"
    f"?query={query}&page=1&sort=1&date_period=1w&website=www,chosun"
)
driver.get(url)
time.sleep(3)

# ====== 기사 블록 탐색 ======
# 조선일보는 div.search-feed 안에 story-card 들이 존재
cards = driver.find_elements(By.CSS_SELECTOR, "div.search-feed div.story-card-wrapper div.story-card")

print(f"📰 총 {len(cards)}개의 기사 감지됨")

visited = set()
count = 0
while True:
    for idx, card in enumerate(cards, 1):
        try:
            link_el = card.find_element(By.CSS_SELECTOR, "a[href]")
            href = link_el.get_attribute("href")

            # 링크 유효성 검사
            if not href or not href.startswith("http") or href in visited:
                continue
            visited.add(href)

            count += 1  # ✅ 실제 저장 시도할 때만 증가
            print(f"\n[{count}] {href} 저장 시도 중...")

            # 새 탭으로 열기
            driver.execute_script(f"window.open('{href}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])

            # 기사 로딩 대기 (랜덤)
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
# ====== 다음 페이지 버튼 탐색 ======
    try:
    # 현재 페이지 번호 가져오기
        current_page = driver.find_element(By.CSS_SELECTOR, "ul.pageNumbers li.active")
        current_num = int(current_page.text.strip())
        print(f"📍 현재 페이지: {current_num}")

        # 다음 페이지 버튼 탐색
        next_btn = driver.find_element(By.CSS_SELECTOR, "div.next button.box--pointer")
        # 버튼이 비활성화되어 있지 않으면 클릭
        next_btn.click()
        print(f"➡️ 다음 페이지로 이동 시도 중 ({current_num + 1}페이지)...")
        time.sleep(3)

        try:
                alert = driver.switch_to.alert
                print(f"⚠️ Alert 감지됨: {alert.text}")
                alert.accept()
                print("✅ 마지막 페이지 도달. 루프 종료.")
               
                
        except:
            # alert이 없으면 그냥 다음 페이지로 넘어감
            pass

    except Exception as e:
        print(f"⚠️ 기타 예외 발생: {e}")
        break
print(f"\n🎉 모든 기사 PDF 저장 완료! ({count}개)")
print(f"📁 저장 경로: {os.path.abspath(save_dir)}")

