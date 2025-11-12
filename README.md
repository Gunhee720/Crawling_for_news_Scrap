# 📰 명지대학교 뉴스 스크래핑 자동화 프로젝트 (MJU News Auto-Scraper)

> **프로젝트 목적:**  
> 네이버, 조선일보, 중앙일보, 한겨레 등 주요 언론사에서 “명지대” 관련 기사를 자동으로 수집하여 PDF로 저장하는 파이프라인을 구축합니다.  
> 수작업으로 2~3시간 걸리던 기사 수집 작업을 **약 25분 내외**로 자동화하였습니다.

---

## 📁 프로젝트 구조
```
├── 명지대_News_PDFSave_v2.py # 네이버 뉴스 1주간 기사 크롤링 + PDF 저장
├── 명지대_News_PDFSave_v3.py # 네이버 뉴스 고도화 버전 (유사도 그룹화, 신문사별 정렬)
├── 조선,중앙,한겨레_NewsScrap.py # 3개 신문사 스크립트 자동 실행 컨트롤러
├── 조선일보_NewsScrap.py # 조선일보 기사 수집 + PDF 저장
├── 중앙일보_NewsScrap.py # 중앙일보 기사 수집 + PDF 저장
├── 한겨레_NewsScrap.py # 한겨레 기사 수집 + PDF 저장
└── README.md
```

---

## ⚙️ 주요 기능

### 1. 네이버 뉴스 스크래퍼 (`명지대_News_PDFSave_v3.py`)
- 최근 **1주일간 “명지대” 관련 기사** 자동 탐색  
- 기사별 PDF 저장  
- 기사 제목 **유사도(>80%) 그룹화**  
- 신문사 우선순위 정렬 (예: 조선일보 → 중앙일보 → 한겨레 등)  
- RapidFuzz 기반 `fuzzy matching` 활용  
<img width="1314" height="1370" alt="스크린샷 2025-11-09 173200" src="https://github.com/user-attachments/assets/42708c16-460a-4540-8da0-46ed8ab484ad" />
<img width="984" height="517" alt="스크린샷 2025-11-09 214913" src="https://github.com/user-attachments/assets/17f4a84c-05e0-4f8a-95cd-d40c520e519b" />
<img width="339" height="313" alt="스크린샷 2025-11-09 224052" src="https://github.com/user-attachments/assets/d5c529d0-2adc-445d-bd9e-1d6397f48db4" />


---

### 2. 개별 신문사 스크래퍼
#### ▫️ 조선일보_NewsScrap.py
- https://www.chosun.com/nsearch  
- “명지대” 키워드 검색 (최근 1주)  
- 각 기사 PDF 자동 저장 및 중복 방지  
- 예외 처리: alert 창 감지 및 페이지 루프 종료  

#### ▫️ 중앙일보_NewsScrap.py
- https://www.joongang.co.kr/search  
- 검색 옵션에서 “1주일” 선택 후 기사 수집  
- 각 기사별 3~6초 랜덤 대기 → 차단 방지  

#### ▫️ 한겨레_NewsScrap.py
- https://search.hani.co.kr/search  
- “기간: 1주일” 필터 적용  
- 기사 리스트 전부 PDF 저장  

---

### 3. 통합 실행 컨트롤러 (`조선,중앙,한겨레_NewsScrap.py`)
- 세 신문사별 스크립트를 **순차 실행**
- subprocess로 각 스크립트 독립 실행
- 로그 출력 및 오류 핸들링 포함

---

## 사용 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python 3.10+ |
| 자동화 | Selenium, Chrome WebDriver |
| 문자열 처리 | re, unicodedata, RapidFuzz |
| 파일 처리 | base64, os, datetime |
| PDF 생성 | Chrome DevTools Protocol (`Page.printToPDF`) |
| 실행 제어 | subprocess, sys |


