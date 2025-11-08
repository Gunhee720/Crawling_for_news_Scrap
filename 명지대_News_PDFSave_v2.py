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
        href = link.get_attribute("href")
        if href and href.startswith("http") and href not in visited:
            visited.add(href)
            try:
                driver.execute_script(f"window.open('{href}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

                # 기사 로딩 시간 랜덤 (1-2초)
                time.sleep(random.uniform(1, 2))
                title_print = driver.title
                # 파일명 정리
                raw_title = driver.title.strip()
                print("raw_title",raw_title)
                # 1️⃣ 언론사명 추출: " - 언론사명" 형태
                press_match = re.search(r"(?:-|::|＞|｜|\||—|‧)\s*([^\-:|>｜‧]+)\s*(?:$|::|-|$)", raw_title)
                press = press_match.group(1).strip() if press_match else ""
                
                # 2️⃣ 기사 제목 부분: '<' 또는 '-' 앞의 주요 제목만 추출
                # <, |, - 구분이 섞여 있는 경우에도 대응
                main_title = re.split(r"[-<|:＞｜‧]", raw_title)[0].strip()

                # 3️⃣ 불필요한 단어 제거 (양쪽에 있어도 전부 제거)
                remove_words = [
                    "대학뉴스", "대학소식", "대학교육", "기사본문", "대학", "뉴스",
                    "보도자료", "기획", "교육뉴스", "언론보도", "공감언론"
                ]
                for w in remove_words:
                    main_title = main_title.replace(w, "")
                    press = press.replace("공감언론", "")
                    press = press.replace("E동아", "동아일보")

                if not press:
                    press = "예상:대학저널"  

                # 4️⃣ 양쪽 공백 정리
                main_title = main_title.strip(" _-·—–")

                # 5️⃣ 파일명 구성
            
                final_title = f"{main_title}_{press}"
            

                # ===========================
                # 🚫 필터링 로직
                # ===========================
                if "명지대" not in main_title:
                    skip_count += 1
                    print(f"⚠️ '{main_title}' → '명지대' 미포함 (누락 {skip_count}/3)")

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    # 🔸 3번 이상 누락 시 종료
                    if skip_count >= 3:
                        print("\n🚨 '명지대' 포함되지 않은 기사가 3회 연속 발견되어 프로그램을 종료합니다.")
                        driver.quit()
                        raise SystemExit
                    continue
                else:
                    # 포함되면 카운트 초기화
                    skip_count = 0

                # 6️⃣ 파일명에서 불법 문자 제거
                safe_title = re.sub(r'[\\/*?:"<>|]', "_", final_title)
                safe_title = re.sub(r'_+', '_', safe_title)   # 여러 개 연속된 '_' → 하나로 축소
                safe_title = safe_title.strip('_ ')

                # 8️⃣ 최종 경로 반환
                filename = os.path.join(save_dir, f"{safe_title}.pdf")
                
                
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

                # 기사 간 랜덤 대기 (2-3초)
                time.sleep(random.uniform(2, 3))

            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")
                driver.switch_to.window(driver.window_handles[0])

print(f"\n✅ 모든 기사 및 관련기사 PDF 저장 완료! ({len(visited)}개 저장됨)")
print(f"📁 저장 경로: {os.path.abspath(save_dir)}")
