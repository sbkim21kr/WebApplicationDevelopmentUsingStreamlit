import streamlit as st
from datetime import datetime
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="MES Dashboard V2", page_icon="🏭", layout="wide")
st.title("🏭 MES 생산 현황 대시보드 V2")
st.markdown("---")

# 세션 상태 초기화
if 'reports' not in st.session_state:
    st.session_state['reports'] = []

# 가상 생산 데이터 및 현황 모니터링
PRODUCTION_TARGET = 3000
current_production = 2350
achievement_rate = (current_production / PRODUCTION_TARGET) * 100
st.header("📊 생산 현황 모니터링")
col1, col2, col3 = st.columns(3)
with col1: st.metric("일일 생산 목표", f"{PRODUCTION_TARGET} 개")
with col2: st.metric("현재 생산량", f"{current_production} 개", delta=f"{current_production - 2300} 개")
with col3: st.metric("달성률", f"{achievement_rate:.2f} %", delta=f"{achievement_rate - 75:.2f} %")
st.progress(achievement_rate / 100)
st.markdown("---")

# 품질/특이사항 보고
st.header("📝 품질/특이사항 보고")
form_col1, form_col2 = st.columns(2)
with form_col1:
    line_option = st.selectbox("생산 라인", ("1번 라인", "2번 라인", "3번 라인"), key="line_select")
    issue_type = st.selectbox("문제 유형", ("단순 불량", "설비 고장", "원료 부족", "기타"), key="issue_select")
    uploaded_image = st.file_uploader("증거 사진 첨부", type=["jpg", "jpeg", "png"], key="image_upload")
with form_col2:
    issue_details = st.text_area("상세 내용 입력", placeholder="문제 상황을 구체적으로 기술하십시오...", key="details_input")
_, center_col, _ = st.columns([2, 1, 2])
with center_col:
    submit_button = st.button("보고서 제출", use_container_width=True)

# 보고서 제출 로직
if submit_button:
    if not issue_details:
        st.warning("상세 내용을 입력해야 합니다.")
    else:
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_data = uploaded_image.getvalue() if uploaded_image is not None else None
        new_report = {
            "time": report_time, "line": line_option, "type": issue_type,
            "details": issue_details, "image": image_data
        }
        st.session_state.reports.append(new_report)
        st.success(f"[{report_time}] 보고서가 성공적으로 제출되었습니다!")

# 제출된 보고서 목록 표시
st.markdown("---")
st.header("📋 최근 제출된 보고서 목록")
if not st.session_state.reports:
    st.info("제출된 보고서가 없습니다.")
else:
    for report in reversed(st.session_state.reports):
        with st.expander(f"[{report['time']}] {report['line']} - {report['type']}"):
            st.text(f"상세 내용: {report['details']}")
            if report['image']:
                st.image(report['image'], caption="첨부된 증거 사진", width=300)

