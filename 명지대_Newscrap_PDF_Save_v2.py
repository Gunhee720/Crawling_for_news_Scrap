from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, base64, os
from datetime import datetime

# ====== 기본 설정 ======
query = "명지대"
today = datetime.now().strftime("%Y%m%d")
save_dir = f"./NewsPDFs/{query}_Scrap_{today}/"

# 폴더 생성
os.makedirs(save_dir, exist_ok=True)

# ====== 브라우저 설정 ======
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query={query}"
driver.get(url)

# 옵션 버튼 클릭
opt_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_option._search_option_open_btn")))
opt_btn.click()
print("✅ 검색 옵션 버튼 클릭 완료")
time.sleep(2)
# '1주' 버튼 클릭
week_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="txt" and text()="1주"]')))
week_btn.click()
time.sleep(2)

# 스크롤 (렌더링 유도)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3)")
time.sleep(2)

# 뉴스 블록 가져오기
news_blocks = driver.find_elements(
    By.CSS_SELECTOR,
    "div.sds-comps-vertical-layout.sds-comps-full-layout[data-template-type='vertical']"
)

print("\n월요일이 왔군요 화이팅!")
print("\n뉴스 스크랩 프로그램을 실행하겠습니다.\n")
print(f"총 {len(news_blocks)}개의 기사 블록 탐색 중...")

visited = set()
i=0
# ====== 기사 반복 ======
for idx, block in enumerate(news_blocks, 1):
    print(f"\n📰 [{idx}] 뉴스 블록 처리 중...")

    # 대표 기사 + 관련 기사 링크
    main_links = block.find_elements(By.CSS_SELECTOR, "a[href][data-heatmap-target='.tit']")
    related_links = block.find_elements(By.CSS_SELECTOR, "div.kKg41qrHvplVksYUiHBW a[href]")
    all_links = main_links + related_links

    for link in all_links:
        i+=1
        if i >= 5:
            break
        href = link.get_attribute("href")
        if href and href.startswith("http") and href not in visited:
            visited.add(href)
            try:
                driver.execute_script(f"window.open('{href}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

                # 기사 로딩 시간 랜덤 (4~7초)
                time.sleep(random.uniform(4, 7))

                # 파일명 정리
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

                filename = os.path.join(save_dir, f"{idx:02d}_{safe_title[:40]}.pdf")

                # 이미 저장된 파일이면 스킵
                if os.path.exists(filename):
                    print(f"⚠️ 이미 저장됨: {filename}")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                print("📄 저장 중:", safe_title)

                # ✅ PDF 저장
                pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
                    "printBackground": True,
                    "landscape": False,
                    "scale": 1
                })
                pdf_bytes = base64.b64decode(pdf_data['data'])

                with open(filename, "wb") as f:
                    f.write(pdf_bytes)

                print(f"✅ PDF 저장 완료: {filename}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                # 기사 간 랜덤 대기 (3~6초)
                import random
                time.sleep(random.uniform(3, 6))

            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")
                driver.switch_to.window(driver.window_handles[0])

print(f"\n✅ 모든 기사 및 관련기사 PDF 저장 완료! ({len(visited)}개 저장됨)")
print(f"📁 저장 경로: {os.path.abspath(save_dir)}")
