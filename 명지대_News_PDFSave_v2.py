from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, base64, os
from datetime import datetime
import random
import re
# ====== 기본 설정 ======
query = "명지대"
today = datetime.now().strftime("%Y%m%d")
save_dir = f"./NewsPDFs/{query}_네이버_{today}/"

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

print("\n이번주도 힘내세요! 💪")
print("\nScraping Program을 실행하겠습니다.\n")
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
        if i >= 20:
            break
        href = link.get_attribute("href")
        if href and href.startswith("http") and href not in visited:
            visited.add(href)
            try:
                driver.execute_script(f"window.open('{href}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

                # 기사 로딩 시간 랜덤 (3~4초)
                time.sleep(random.uniform(1, 2))
                
                # 파일명 정리
                raw_title = driver.title.strip()
                
                # ✅ 언론사 추출 정규식
                # 패턴: "... 기사제목 ... - 언론사" 또는 "... :: 언론사"
                patterns = [
                    r"(.+?)\s*-\s*(.+)",            # 제목 - 언론사
                    r"(.+?)\s*::\s*(.+)",           # 제목 :: 언론사
                ]
                title = raw_title
                source = "Unknown"

                for p in patterns:
                    match = re.match(p, raw_title)
                    if match:
                        title = match.group(1).strip()
                        source = match.group(2).strip()
                        break

                # ✅ 특정 언론사 치환 규칙
                source = source.replace("공감언론 뉴시스", "뉴시스")

                # ✅ 기사 소스가 네이버 내부 경로로 나오는 경우 제거
                noise_words = ["대학뉴스", "대학", "기사본문", "대학소식", "대학교육", "매일일보"]
                if any(w in source for w in noise_words):
                    source = "Unknown"
                # ✅ 파일명 안전 문자 처리  
                def safe(s):
                    return re.sub(r'[\\/:*?"<>|]', '_', s).replace("__", "_").strip()

                filename = os.path.join(save_dir, f"{safe(title)}_{safe(source)}.pdf")

                
                
                # 이미 저장된 파일이면 스킵
                if os.path.exists(filename):
                    print(f"⚠️ 이미 저장됨: {filename}")
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

                print(f"✅저장: {filename}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                # 기사 간 랜덤 대기 (3~4초)
                time.sleep(random.uniform(2, 3))

            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")
                driver.switch_to.window(driver.window_handles[0])

print(f"\n✅ 모든 기사 및 관련기사 PDF 저장 완료! ({len(visited)}개 저장됨)")
print(f"📁 저장 경로: {os.path.abspath(save_dir)}")
