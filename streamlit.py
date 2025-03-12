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

# Add Open Graph meta tags
st.markdown("""
    <head>
        <meta property="og:title" content="단독뉴스 모니터링">
        <meta property="og:description" content="실시간 단독뉴스 모니터링 서비스">
        <meta property="og:image" content="https://cdn.pixabay.com/photo/2015/11/06/15/13/news-1028791_1280.jpg">
        <meta property="og:url" content="https://gq-exnews.streamlit.app">
    </head>
""", unsafe_allow_html=True)

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
        
        # 카테고리별 색상 정의
        category_colors = {
            '정치': '#FF5A5A',  # 빨간색 계열
            '경제': '#5ABD5A',  # 녹색 계열
            '사회': '#5A7DFF',  # 파란색 계열
            '문화': '#FF9E5A',  # 주황색 계열
            '국제': '#9D5AFF',  # 보라색 계열
            '연예/스포츠': '#FF5AE5',  # 분홍색 계열
            '기타': '#8E8E8E'   # 회색 계열
        }
        
        # 날짜 형식 변환 및 카테고리 처리
        for item in news_items:
            try:
                # float나 다른 타입을 문자열로 변환
                pub_date = str(item['pubDate']).strip()
                # RFC 2822 형식의 날짜 문자열을 datetime 객체로 변환
                date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                # 원하는 형식으로 변환
                item['pubDate'] = date_obj.strftime('%Y년 %m월 %d일 %p %I시 %M분').replace('AM', '오전').replace('PM', '오후')
            except (ValueError, TypeError):
                # 날짜 변환에 실패한 경우 기본값 설정
                item['pubDate'] = '날짜 정보 없음'
            
            # 카테고리가 없거나 NaN인 경우 '기타'로 설정
            if 'category' not in item or not item['category'] or str(item['category']).lower() == 'nan':
                item['category'] = '기타'
            
            # 카테고리에 색상 정보 추가
            item['category_color'] = category_colors.get(item['category'], '#8E8E8E')  # 기본값은 회색
            
        # 최신순으로 정렬 (날짜 정보 없는 항목은 마지막으로)
        news_items.sort(key=lambda x: datetime.strptime(x['pubDate'].replace('오전', 'AM').replace('오후', 'PM'), 
                                                      '%Y년 %m월 %d일 %p %I시 %M분') if x['pubDate'] != '날짜 정보 없음' 
                                                      else datetime.min, reverse=True)
        return news_items
    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return []

def main():
    st.title("🔍 이시간 단독뉴스")
    st.markdown("---")
    
    # 관리자 공지 섹션 추가
    st.info("- 5분 간격으로 업데이트 됩니다!\n- 업데이트 중에 일부 기사가 중복해서 보일 수 있습니다. \n- 문의 : GQ.newslens@gmail.com \n- 국회 앞 식당정보 https://na-res.streamlit.app/")
    
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
    
    /* 카테고리 스타일 - 기본 스타일 */
    .news-category {
        display: inline-block;
        color: white;
        font-size: 10px;
        padding: 1px 8px;
        border-radius: 12px;
        margin-right: 8px;
    }
    
    /* 카테고리 필터 스타일 */
    .category-filter {
        margin-bottom: 15px;
    }
    
    /* 카테고리 버튼 스타일 */
    div.stRadio > div {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    div.stRadio > div > label {
        border-radius: 15px;
        padding: 3px 10px;
        cursor: pointer;
        margin: 0;
        transition: all 0.2s;
        background-color: transparent;
        border: 1.5px solid;
        font-size: 0.85rem;
    }
    
    div.stRadio > div > label:hover {
        opacity: 0.8;
        background-color: rgba(0, 0, 0, 0.05);
    }
    
    div.stRadio > div > label[data-baseweb="radio"] > div:first-child {
        display: none;
    }
    
    /* 카테고리 버튼 색상 */
    div.stRadio > div > label:nth-of-type(1) { color: #666; border-color: #666; } /* 전체 */
    div.stRadio > div > label:nth-of-type(2) { color: #FF5A5A; border-color: #FF5A5A; } /* 정치 */
    div.stRadio > div > label:nth-of-type(3) { color: #5ABD5A; border-color: #5ABD5A; } /* 경제 */
    div.stRadio > div > label:nth-of-type(4) { color: #5A7DFF; border-color: #5A7DFF; } /* 사회 */
    div.stRadio > div > label:nth-of-type(5) { color: #FF9E5A; border-color: #FF9E5A; } /* 문화 */
    div.stRadio > div > label:nth-of-type(6) { color: #9D5AFF; border-color: #9D5AFF; } /* 국제 */
    div.stRadio > div > label:nth-of-type(7) { color: #FF5AE5; border-color: #FF5AE5; } /* 연예/스포츠 */
    div.stRadio > div > label:nth-of-type(8) { color: #8E8E8E; border-color: #8E8E8E; } /* 기타 */
    
    /* 선택된 버튼 스타일 */
    div.stRadio > div > label[aria-checked="true"] {
        background-color: currentColor;
        color: white;
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
    
    # 카테고리 필터 추가
    if st.session_state['news_items']:
        # 모든 카테고리 추출
        all_categories = []
        for item in st.session_state['news_items']:
            if item['category'] not in all_categories:
                all_categories.append(item['category'])
        
        # 카테고리가 있는 경우에만 필터 표시
        if all_categories:
            # 지정된 카테고리 순서 정의
            category_order = ['전체', '정치', '경제', '사회', '문화', '국제', '연예/스포츠', '기타']
            
            # 모든 카테고리 중에서 지정된 순서에 있는 것만 먼저 추가
            ordered_categories = ['전체']
            for category in category_order[1:]:  # '전체'는 이미 추가했으므로 제외
                if category in all_categories:
                    ordered_categories.append(category)
            
            # 지정된 순서에 없는 나머지 카테고리들을 알파벳 순으로 추가
            remaining_categories = [cat for cat in all_categories if cat not in category_order]
            remaining_categories.sort()
            ordered_categories.extend(remaining_categories)
            
            # 라디오 버튼으로 카테고리 필터 구현
            st.markdown('<div class="category-filter">', unsafe_allow_html=True)
            selected_category = st.radio(
                "카테고리",
                ordered_categories,
                index=0,
                label_visibility="collapsed",
                horizontal=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 선택된 카테고리에 따라 필터링
            if selected_category == '전체':
                filtered_items = st.session_state['news_items']
            else:
                filtered_items = [item for item in st.session_state['news_items'] 
                                if 'category' in item and item['category'] == selected_category]
        else:
            filtered_items = st.session_state['news_items']
    else:
        filtered_items = []
    
    # 뉴스 아이템 표시
    if filtered_items:
        for idx, item in enumerate(filtered_items):
            with st.container():
                # 90:10 비율의 컬럼 생성
                cols = st.columns([9, 1])
                
                # 왼쪽 컬럼: 제목과 날짜
                with cols[0]:
                    st.markdown(
                        f'<div class="news-title"><a href="{item["link"]}" target="_blank" style="text-decoration:none; color:inherit;">{item["title"]}</a></div>',
                        unsafe_allow_html=True
                    )
                    
                    # 카테고리와 날짜 정보 표시
                    category_html = f'<span class="news-category" style="background-color: transparent; color: #555555; border: 1px solid #AAAAAA; padding: 1px 8px;">{item["category"]}</span>'
                    st.markdown(f'<div class="news-date">{category_html}⏰ {item["pubDate"]}</div>', unsafe_allow_html=True)
                
                # 오른쪽 컬럼: 링크 아이콘
                with cols[1]:
                    st.markdown(f'<a href="{item["link"]}" target="_blank">🔗</a>', unsafe_allow_html=True)
                
                # 뉴스 아이템 구분선
                if idx < len(filtered_items) - 1:
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
