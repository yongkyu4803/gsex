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
    # JavaScript 코드가 실행될 때 텍스트를 이스케이프
    escaped_text = text.replace('`', '\\`').replace('\n', '\\n')
    
    js_code = f"""
    <script>
        function copyToClipboard() {{
            try {{
                navigator.clipboard.writeText(`{escaped_text}`).then(
                    function() {{
                        window.parent.postMessage({{type: "copySuccess", idx: {idx}}}, "*");
                    }}, 
                    function(err) {{
                        console.error('클립보드 복사 실패:', err);
                    }}
                );
            }} catch (err) {{
                console.error('클립보드 복사 오류:', err);
            }}
        }}
        // 페이지 로드 시 실행
        window.onload = copyToClipboard;
    </script>
    """
    
    st.components.v1.html(js_code, height=0)
    st.session_state[f'copied_{idx}'] = True
    # 3초 후에 복사 상태를 원래대로 되돌리기 위한 타임스탬프 설정
    st.session_state[f'reset_time_{idx}'] = time.time() + 3

def main():
    st.title("🔍 이시간 단독뉴스")
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
    
    # 복사 상태 리셋 처리 (타이머 기반)
    current_time = time.time()
    for idx in range(len(st.session_state.get('news_items', []))):
        reset_key = f'reset_time_{idx}'
        if reset_key in st.session_state and current_time > st.session_state[reset_key]:
            st.session_state[f'copied_{idx}'] = False
            del st.session_state[reset_key]
    
    # 이벤트 리스너 설정 (JavaScript와 통신하기 위한 코드)
    event_listener = """
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'copySuccess') {
                // 스트림릿에 메시지 전달
                window.parent.postMessage({type: "streamlit:setComponentValue", value: true}, "*");
            }
        });
    </script>
    """
    st.components.v1.html(event_listener, height=0)
    
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
                    
                    if st.button(
                        button_label, 
                        key=f"copy_{idx}", 
                        help="클립보드에 복사"
                    ):
                        copy_to_clipboard(copy_text, idx)
                        st.toast("클립보드에 복사되었습니다!")
                
                # 구분선 추가
                if idx < len(st.session_state['news_items']) - 1:
                    st.markdown('<hr style="margin: 5px 0; border: 0; height: 1px; background-color: #e0e0e0;">', unsafe_allow_html=True)
    
    else:
        if 'first_load' in st.session_state:
            st.info("새로운 단독뉴스가 없습니다.")
    
    # Add footer
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