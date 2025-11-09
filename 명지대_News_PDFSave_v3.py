from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, base64, os, random, re
from datetime import datetime
from rapidfuzz import fuzz  # ✅ 추가: 제목 유사도 비교용

# 유사도를 위한 기사 정규화
import unicodedata

# 기사 제목 정규화 함수
def normalize_title(t):
    t = t.lower()
    t = unicodedata.normalize('NFKC', t)  # ‘ ’ → ' 로 통일
    t = re.sub(r"[^가-힣a-z0-9\s]", "", t)  # 특수문자 제거
    return t.strip()

# 유사도 계산 함수
def similarity(a, b):
    a_n, b_n = normalize_title(a), normalize_title(b)
    return (fuzz.partial_ratio(a_n, b_n) * 0.6 +
            fuzz.token_set_ratio(a_n, b_n) * 0.4)


# ====== 기본 설정 ======
query = "명지대"
today = datetime.now().strftime("%Y%m%d")
save_dir = f"./NewsPDFs/{query}_네이버_{today}/"

os.makedirs(save_dir, exist_ok=True)

# 언론사 우선순위 리스트
PRESS_ORDER = [
    "조선일보", "중앙일보", "동아일보", "한겨레", "머니투데이", "내일신문",
    "뉴시스", "베리타스알파", "매일일보", "대학저널", "뉴데일리", "한국대학신문", "비욘드포스트"
]

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

# 뉴스 블록 탐색
news_blocks = driver.find_elements(
    By.CSS_SELECTOR,
    "div.sds-comps-vertical-layout.sds-comps-full-layout[data-template-type='vertical']"
)

print("\n📰 Scraping Program을 실행하겠습니다.\n")
print(f"총 {len(news_blocks)}개의 뉴스 블록 탐색 중...\n")

visited = set()
articles = []   # ✅ 모든 기사 데이터를 메모리에 저장
skip_count = 0
i = 0

# ====== 기사 반복 ======
for idx, block in enumerate(news_blocks, 1):
    print(f"🧩 [{idx}] 뉴스 블록 처리 중...")

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
                time.sleep(random.uniform(1, 2))

                raw_title = driver.title.strip()
                print("raw_title", raw_title)

                # 언론사명 추출
                press_match = re.search(
                    r"(?:\s*(?:-|::|:|＞|｜|\||—|‧)\s*)([가-힣A-Za-z0-9&·\s]+?)\s*(?:(?:[:：]{2,}|-)?\s*)$",
                    raw_title
                )
                press = press_match.group(1).strip() if press_match else ""
                print("신문사", press)

                # 제목 정리
                main_title = re.split(r"[-<|:＞｜‧]", raw_title)[0].strip()
                remove_words = ["대학뉴스", "대학소식", "대학교육", "기사본문", "대학", "뉴스", "보도자료", "기획", "교육뉴스", "언론보도", "공감언론"]
                for w in remove_words:
                    main_title = main_title.replace(w, "")
                    press = press.replace("공감언론", "")
                    press = press.replace("E동아", "동아일보")
                if not press:
                    press = "대학저널,점프볼같은 구조없는 신문사"
                main_title = main_title.strip(" _-·—–")

                # 명지대 필터링
                if "명지대" not in main_title:
                    skip_count += 1
                    print(f"⚠️ '{main_title}' → '명지대' 미포함 (누락 {skip_count}/3)")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    if skip_count >= 3:
                        print("\n🚨 '명지대' 미포함 기사 3회 연속 → 종료")
                        break
                    continue
                else:
                    skip_count = 0

                # PDF 저장 대신 메모리에 담기
                pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {
                    "printBackground": True,
                    "landscape": False,
                    "scale": 1
                })
                pdf_bytes = base64.b64decode(pdf_data["data"])

                articles.append({
                    "main_title": main_title,
                    "press": press,
                    "pdf_bytes": pdf_bytes
                })
                print(f"🗂 임시 저장: {main_title} ({press})")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(random.uniform(2, 3))

            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")
                driver.switch_to.window(driver.window_handles[0])

# ====== 모든 기사 수집 후 그룹화 ======
print(f"\n✅ 기사 수집 완료 ({len(articles)}개)\n")
print("📂 유사 제목 그룹화 및 폴더 정리 중...\n")

grouped = []
for art in articles:
    placed = False
    for g in grouped:
        if similarity(art["main_title"], g["rep"]) > 80:
            g["items"].append(art)
            placed = True
            break
    if not placed:
        grouped.append({"rep": art["main_title"], "items": [art]})

for g in grouped:
    folder_name = re.sub(r'[\\/*?:"<>|]', "_", g["rep"].strip())
    folder_path = os.path.join(save_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)

     # ✅ 저장 순서를 신문사 기준으로 정렬
    g["items"].sort(
        key=lambda x: PRESS_ORDER.index(x["press"]) if x["press"] in PRESS_ORDER else len(PRESS_ORDER)
    )

    for art in g["items"]:
        press_clean = re.sub(r'[\\/*?:"<>|]', "_", art["press"].strip())
        pdf_path = os.path.join(folder_path, f"{press_clean}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(art["pdf_bytes"])
        print(f"✅ {press_clean}.pdf - ({folder_name})")

print("\n🎉 모든 유사 기사 폴더 정리 완료!")
print(f"📁 최종 저장 경로: {os.path.abspath(save_dir)}")
print(f"\n✅ 모든 기사 및 관련기사 PDF 저장 완료! ({len(visited)}개 저장됨)")
