from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

query = "명지대"
url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query={query}"
driver.get(url)

# 옵션 버튼 클릭
opt_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_option._search_option_open_btn")))
opt_btn.click()

# '1주' 버튼 클릭
week_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="txt" and text()="1주"]')))
week_btn.click()
time.sleep(2)

# 스크롤 (렌더링 유도)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3)")
time.sleep(2)

# ✅ 모든 뉴스 블록 가져오기 (동적 class 대신 안정적 구조 사용)
news_blocks = driver.find_elements(
    By.CSS_SELECTOR,
    "div.sds-comps-vertical-layout.sds-comps-full-layout[data-template-type='vertical']"
)

print(f"총 {len(news_blocks)}개의 기사 블록 탐색 중...")

visited = set()

for idx, block in enumerate(news_blocks, 1):
    print(f"\n📰 [{idx}] 뉴스 블록 처리 중...")

    # 대표 기사 링크
    main_links = block.find_elements(By.CSS_SELECTOR, "a[href][data-heatmap-target='.tit']")
    # 관련 기사 링크
    related_links = block.find_elements(By.CSS_SELECTOR, "div.kKg41qrHvplVksYUiHBW a[href]")

    all_links = main_links + related_links

    for link in all_links:
        href = link.get_attribute("href")
        if href and href.startswith("http") and href not in visited:
            visited.add(href)
            try:
                print("\n")
                driver.execute_script(f"window.open('{href}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(4)
                print("제목:", driver.title)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ 오류 발생: {e}")
                driver.switch_to.window(driver.window_handles[0])

print("\n✅ 모든 기사 및 관련기사 방문 완료!")
