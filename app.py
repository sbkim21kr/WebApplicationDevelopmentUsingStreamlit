import streamlit as st
from datetime import datetime
import pandas as pd # Pandas 추가

# 페이지 설정, 제목 등 (이전과 동일)
st.set_page_config(page_title="MES Dashboard V2", page_icon="🏭", layout="wide")
st.title("🏭 MES 생산 현황 대시보드 V2")
st.markdown("---")

# --- 세션 상태 초기화 ---
# 'reports' 키가 존재하지 않으면 빈 리스트로 초기화
if 'reports' not in st.session_state:
    st.session_state['reports'] = []

# 가상 생산 데이터 및 현황 모니터링 (이전과 동일)
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

# 품질/특이사항 보고 (업그레이드)
st.header("📝 품질/특이사항 보고")
form_col1, form_col2 = st.columns(2)

with form_col1:
    # 위젯에 고유 key 지정 (상태 관리에 유용)
    line_option = st.selectbox("생산 라인", ("1번 라인", "2번 라인", "3번 라인"), key="line_select")
    issue_type = st.selectbox("문제 유형", ("단순 불량", "설비 고장", "원료 부족", "기타"), key="issue_select")
    # 파일 업로더 추가
    uploaded_image = st.file_uploader("증거 사진 첨부", type=["jpg", "jpeg", "png"], key="image_upload")
with form_col2:
    issue_details = st.text_area("상세 내용 입력", placeholder="문제 상황을 구체적으로 기술하십시오...", key="details_input")

_, center_col, _ = st.columns([2, 1, 2])
with center_col:
    submit_button = st.button("보고서 제출", use_container_width=True)

# 보고서 제출 로직 (업그레이드)
if submit_button:
    if not issue_details:
        st.warning("상세 내용을 입력해야 합니다.")
    else:
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_data = None
        if uploaded_image is not None:
            image_data = uploaded_image.getvalue() # 이미지 데이터를 바이트로 읽기

        # 새로운 보고서 데이터를 세션 상태 리스트에 추가
        new_report = {
            "time": report_time,
            "line": line_option,
            "type": issue_type,
            "details": issue_details,
            "image": image_data
        }
        st.session_state.reports.append(new_report)
        st.success(f"[{report_time}] 보고서가 성공적으로 제출되었습니다!")

# --- 제출된 보고서 목록 표시 ---
st.markdown("---")
st.header("📋 최근 제출된 보고서 목록")

if not st.session_state.reports:
    st.info("제출된 보고서가 없습니다.")
else:
    # 최신 보고서부터 역순으로 표시
    for report in reversed(st.session_state.reports):
        with st.expander(f"[{report['time']}] {report['line']} - {report['type']}"):
            st.text(f"상세 내용: {report['details']}")
            if report['image']:
                # 첨부된 이미지 표시
                st.image(report['image'], caption="첨부된 증거 사진", width=300)

# --- 사이드바 필터 ---
st.sidebar.header("🔍 필터")

# 보고서 데이터가 있을 경우에만 필터 활성화
if st.session_state.reports:
    # 데이터프레임 변환 (필터링을 위해)
    df_reports = pd.DataFrame(st.session_state.reports)
    
    # 생산 라인 필터 (다중 선택)
    unique_lines = df_reports['line'].unique()
    selected_lines = st.sidebar.multiselect(
        '생산 라인',
        options=unique_lines,
        default=unique_lines
    )

    # 문제 유형 필터 (다중 선택)
    unique_types = df_reports['type'].unique()
    selected_types = st.sidebar.multiselect(
        '문제 유형',
        options=unique_types,
        default=unique_types
    )
else:
    st.sidebar.info("보고서 제출 시 필터가 활성화됩니다.")

# --- 데이터 분석 및 시각화 ---
st.markdown("---")
st.header("🔬 데이터 분석 및 시각화")

if st.session_state.reports:
    df_reports = pd.DataFrame(st.session_state.reports) # 위에서 생성된 df_reports 사용
    
    # 필터 적용
    filtered_df = df_reports[
        df_reports['line'].isin(selected_lines) &
        df_reports['type'].isin(selected_types)
    ]

    if filtered_df.empty:
        st.warning("선택된 조건에 해당하는 데이터가 없습니다.")
    else:
        # 원본 데이터 표시 (선택 사항)
        if st.checkbox("전체 보고 데이터 보기"):
            # 이미지 열은 제외하고 표시
            st.dataframe(filtered_df.drop(columns=['image']))

        st.write("---")
        st.write("#### 차트 분석")
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.write("##### 📊 문제 유형별 발생 빈도")
            issue_counts = filtered_df['type'].value_counts()
            st.bar_chart(issue_counts)
            
        with viz_col2:
            st.write("##### 📈 라인별 보고 건수")
            # Plotly를 사용한 파이 차트 (Plotly 설치 필요: pip install plotly)
            # import plotly.express as px # 코드 상단에 추가
            line_counts = filtered_df['line'].value_counts()
            fig = px.pie(values=line_counts.values, names=line_counts.index, title='라인별 보고 비율')
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("분석할 데이터가 없습니다. 먼저 보고서를 제출하십시오.")

