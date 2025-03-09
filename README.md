# 단독뉴스 모니터링 애플리케이션 📰

## 소개
이 애플리케이션은 Google Sheets에서 단독뉴스 데이터를 실시간으로 모니터링하고 표시하는 Streamlit 기반 웹 애플리케이션입니다.

## 주요 기능
- 📊 Google Sheets에서 실시간 뉴스 데이터 동기화
- 🔄 5분마다 자동 데이터 갱신
- 📋 뉴스 제목, 링크, 날짜 원클릭 복사 기능
- 📱 모바일 친화적인 반응형 디자인
- ⚡ 실시간 업데이트 알림

## 설치 방법
1. 필요한 패키지 설치:
```bash
pip install streamlit pandas pyperclip


## 사용 방법
1. 애플리케이션이 실행되면 자동으로 최신 뉴스 데이터를 불러옵니다.
2. 🔄 버튼을 클릭하여 수동으로 데이터를 새로고침할 수 있습니다.
3. 각 뉴스 항목의 📋 버튼을 클릭하여 뉴스 정보를 클립보드에 복사할 수 있습니다.
4. 뉴스 제목을 클릭하면 해당 기사 페이지로 이동합니다.

## 기술 스택
- Python
- Streamlit
- Pandas
- Google Sheets API

## 환경 설정
애플리케이션을 실행하기 전에 Google Sheets ID를 설정해야 합니다.
현재 설정된 Spreadsheet ID: 1rymOVrvXUltUCIcaY-hhDLV9J05LcV7cPAX0Nt8IHsI