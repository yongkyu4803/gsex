import os
import time
import streamlit as st
import pandas as pd
from datetime import datetime
import pyperclip

# 초기 설정 (모바일 최적화 보기)
st.set_page_config(
    page_title="단독뉴스 모니터링",
    page_icon="📰",
    layout="centered"
)

# 환경 변수 로드
# Google Sheets API 설정
SPREADSHEET_ID='1rymOVrvXUltUCIcaY-hhDLV9J05LcV7cPAX0Nt8IHsI'

@st.cache_data(ttl=300)  # 5분마다 데이터 갱신
def fetch_sheet_data():
    """구글 시트에서 뉴스 데이터 가져오기"""
    try:
        # 구글 시트 URL 생성
        sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
        
        # pandas로 데이터 읽기
        df = pd.read_csv(sheet_url)
        
        # 데이터프레임을 딕셔너리 리스트로 변환
        news_items = df.to_dict('records')
        
        # 최신순으로 정렬
        news_items.sort(key=lambda x: x['pubDate'], reverse=True)
        
        return news_items
    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return []

def copy_to_clipboard(text, idx):
    """클립보드에 텍스트 복사하고 상태 업데이트"""
    pyperclip.copy(text)
    st.session_state[f'copied_{idx}'] = True
    st.session_state[f'reset_scheduled_{idx}'] = True

def main():
    st.title("🔍 단독뉴스")
    st.markdown("---")

    # 세션 상태 초기화
    if 'news_items' not in st.session_state:
        st.session_state['news_items'] = []

    # 새로고침 버튼 배치
    refresh_clicked = st.button("🔄")
    
    # CSS 스타일 적용
    st.markdown("""
    <style>
    /* 뉴스 박스 컨테이너 스타일 */
    .news-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        max-width: 600px;
        width: 95%;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 제목 스타일 */
    .news-title {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 6px;
        line-height: 1.4;
        word-break: keep-all;
    }
    
    /* 날짜 스타일 */
    .news-date {
        color: #666;
        font-size: 14px;
    }
    
    /* 복사 버튼 스타일 */
    .stButton button {
        border-radius: 50%;
        width: 36px !important;
        height: 36px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Streamlit 컬럼 간격 조정 */
    .row-widget.stHorizontal div {
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 페이지 로드 시와 새로고침 버튼 클릭 시 뉴스 불러오기
    if refresh_clicked or 'first_load' not in st.session_state:
        st.session_state['first_load'] = True
        with st.spinner("뉴스를 가져오는 중..."):
            st.session_state['news_items'] = fetch_sheet_data()
    
    # 예약된 초기화 처리
    for idx in range(len(st.session_state.get('news_items', []))):
        reset_key = f'reset_scheduled_{idx}'
        if st.session_state.get(reset_key, False):
            st.session_state[f'copied_{idx}'] = False
            st.session_state[reset_key] = False
    
    # 뉴스 아이템 표시
    if st.session_state['news_items']:
        for idx, item in enumerate(st.session_state['news_items']):
            # 뉴스 컨테이너
            with st.container():
                # 복사 상태 초기화
                if f'copied_{idx}' not in st.session_state:
                    st.session_state[f'copied_{idx}'] = False
                
                # 90:10 비율의 컬럼 생성
                cols = st.columns([9, 1])
                
                # 왼쪽 컬럼: 제목과 날짜
                with cols[0]:
                    # 제목 (링크 포함)
                    st.markdown(f'<div class="news-title"><a href="{item["link"]}" target="_blank" style="text-decoration:none; color:inherit;">{item["title"]}</a></div>', unsafe_allow_html=True)
                    # 날짜
                    st.markdown(f'<div class="news-date">⏰ {item["pubDate"]}</div>', unsafe_allow_html=True)
                
                # 오른쪽 컬럼: 복사 버튼
                with cols[1]:
                    copy_text = f"{item['title']}\n{item['link']}\n{item['pubDate']}"
                    button_label = "✓" if st.session_state[f'copied_{idx}'] else "📋"
                    
                    st.button(
                        button_label, 
                        key=f"copy_{idx}", 
                        on_click=copy_to_clipboard, 
                        args=(copy_text, idx)
                    )
                    
                    if st.session_state[f'copied_{idx}']:
                        st.toast("클립보드에 복사되었습니다!")
                
                # 구분선 추가
                if idx < len(st.session_state['news_items']) - 1:
                    st.markdown('<hr style="margin: 5px 0; border: 0; height: 1px; background-color: #e0e0e0;">', unsafe_allow_html=True)
    
    else:
        if 'first_load' in st.session_state:
            st.info("새로운 단독뉴스가 없습니다.")

if __name__ == "__main__":
    main()