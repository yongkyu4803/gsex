import os
import time
import streamlit as st
import pandas as pd
from datetime import datetime

# 초기 설정 (모바일 최적화 보기)
st.set_page_config(
    page_title="단독뉴스 모니터링",
    page_icon="📰",
    layout="centered"
)

# 환경 변수 로드
# Google Sheets API 설정
SPREADSHEET_ID = '1rymOVrvXUltUCIcaY-hhDLV9J05LcV7cPAX0Nt8IHsI'

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

def main():
    st.title("🔍 이시간 단독뉴스")
    st.markdown("---")
    
    # 관리자 공지 섹션 추가
    st.info("test")
    
    # 세션 상태 초기화
    if 'news_items' not in st.session_state:
        st.session_state['news_items'] = []
    
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
    
    /* Streamlit 컬럼 간격 조정 */
    .row-widget.stHorizontal div {
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 페이지 로드 시 뉴스 불러오기
    if 'first_load' not in st.session_state:
        st.session_state['first_load'] = True
        with st.spinner("뉴스를 가져오는 중..."):
            st.session_state['news_items'] = fetch_sheet_data()
    
    # 뉴스 아이템 표시
    if st.session_state['news_items']:
        for idx, item in enumerate(st.session_state['news_items']):
            with st.container():
                # 90:10 비율의 컬럼 생성
                cols = st.columns([9, 1])
                
                # 왼쪽 컬럼: 제목과 날짜
                with cols[0]:
                    st.markdown(
                        f'<div class="news-title"><a href="{item["link"]}" target="_blank" style="text-decoration:none; color:inherit;">{item["title"]}</a></div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f'<div class="news-date">⏰ {item["pubDate"]}</div>', unsafe_allow_html=True)
                
                # 오른쪽 컬럼: 링크 아이콘
                with cols[1]:
                    st.markdown(f'<a href="{item["link"]}" target="_blank">🔗</a>', unsafe_allow_html=True)
                
                # 뉴스 아이템 구분선
                if idx < len(st.session_state['news_items']) - 1:
                    st.markdown('<hr style="margin: 5px 0; border: 0; height: 1px; background-color: #e0e0e0;">', unsafe_allow_html=True)
    else:
        if 'first_load' in st.session_state:
            st.info("새로운 단독뉴스가 없습니다.")
    
    # Footer 추가
    st.markdown("---")
    st.markdown("""
        <style>
        .footer {
            text-align: center;
            color: #666;
            font-size: 14px;
            padding: 20px 0;
        }
        </style>
        <p class='footer'>Made by GQ 💡</p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
