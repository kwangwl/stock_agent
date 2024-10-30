import streamlit as st
import agent_lib as glib
import pandas as pd
import uuid
import json
import plotly.graph_objects as go
import os
import guardrails
import re


AGENT_ID = st.secrets["AGENT_ID"]
ALIAS_ID = {
    "Sonnet 3.5 v2": st.secrets["BWB_AGENT_ALIAS_ID_3"],
    "Sonnet 3.5 v1": st.secrets["BWB_AGENT_ALIAS_ID_2"],
    "Sonnet 3.0": st.secrets["BWB_AGENT_ALIAS_ID_1"],
}


# function
def display_today(trace_container, trace):
    today_date = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    today_date = json.loads(today_date)

    trace_container.markdown("**오늘의 날짜**")
    trace_container.write(f"{today_date}")


def display_company_profile(trace_container, trace):
    company_profile = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    company_profile = json.loads(company_profile)
    df = pd.DataFrame.from_dict(company_profile, orient='index',columns=['정보'])

    # 주식 정보
    trace_container.markdown("**회사 프로필**")
    trace_container.dataframe(df, use_container_width=True)


def display_stock_chart(trace_container, trace):
    chart_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    chart_data = json.loads(chart_text)

    # DataFrame 생성
    df = pd.DataFrame.from_dict(chart_data, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()  # 날짜순으로 정렬

    # Plotly를 사용한 캔들스틱 차트 생성
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']
            )
        ]
    )
    fig.update_layout(xaxis_title='날짜', yaxis_title='가격')

    # 차트 출력
    trace_container.markdown("**캔들 차트**")
    trace_container.plotly_chart(fig)


def display_stock_balance(trace_container, trace):
    balance_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    balance = json.loads(balance_text)

    df = pd.DataFrame.from_dict(balance, orient='index').transpose()

    # 재무 제표 출력
    trace_container.markdown("**재무 재표**")
    trace_container.dataframe(df, use_container_width=True)


def display_recommendations(trace_container, trace):
    recommendations_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    recommendations = json.loads(recommendations_text)

    df = pd.DataFrame.from_dict(recommendations, orient='index').transpose()

    # 추천 정보 출력
    trace_container.markdown("**애널리스트 추천 정보**")
    trace_container.dataframe(df, use_container_width=True)


# main page
st.set_page_config(page_title="Stock Analyzer")
st.title("Bedrock Agent 주식 분석")

selected_option = st.sidebar.radio(
    "FM 모델을 선택하세요:",
    list(ALIAS_ID.keys())
)

# architecture
with st.expander("아키텍처", expanded=True):
    st.image(os.path.join("static", "Picture3.png"))

input_text = st.text_input("종목명을 입력하세요 (✅ 기업명 입력 가능 / ⚠️ 암호화폐 관련 검색 제한)")
submit_button = st.button("분석 시작", type="primary")

# 실시간 업데이트를 위한 자리 만들기
trace_container = st.container()

if submit_button and input_text:
    with st.spinner("응답 생성 중..."):
        # 에이전트 호출 (세션은 항상 초기화 하도록 구성)
        response = glib.get_agent_response(
            AGENT_ID,
            ALIAS_ID[selected_option],
            str(uuid.uuid4()),
            input_text
        )

        trace_container.subheader("Bedrock Reasoning")

        output_text = ""
        function_name = ""

        for event in response.get("completion"):
            # Combine the chunks to get the output text
            if "chunk" in event:
                chunk = event["chunk"]
                output_text += chunk["bytes"].decode()

            # Extract trace information from all events
            if "trace" in event:
                # st.json(event["trace"])
                each_trace = event["trace"]["trace"]

                if "orchestrationTrace" in each_trace:
                    trace = event["trace"]["trace"]["orchestrationTrace"]

                    if "rationale" in trace:
                        with trace_container.chat_message("ai"):
                            st.markdown(trace['rationale']['text'])

                    elif function_name != "":
                        if function_name == "get_today":
                            display_today(trace_container, trace)

                        elif function_name == "get_company_profile":
                            display_company_profile(trace_container, trace)

                        elif function_name == "get_stock_chart":
                            display_stock_chart(trace_container, trace)

                        elif function_name == "get_stock_balance":
                            display_stock_balance(trace_container, trace)

                        elif function_name == "get_recommendations":
                            display_recommendations(trace_container, trace)

                        function_name = ""

                    else:
                        function_name = trace.get('invocationInput', {}).get('actionGroupInvocationInput', {}).get(
                            'function', "")

                elif "guardrailTrace" in each_trace:
                    guardrails.display_guardrail_trace(trace_container, each_trace["guardrailTrace"])

                # trace_container.json(event["trace"]["trace"])

        # 응답 출력
        trace_container.divider()
        trace_container.subheader("Analysis Report")
        # {TEXT} 패턴을 찾아서 스타일이 적용된 HTML로 변경
        styled_text = re.sub(
            r'\{([^}]+)\}',
            r'<span style="background-color: #ffd700; padding: 2px 6px; border-radius: 3px; font-weight: bold; color: #1e1e1e;">\1</span>',
            output_text
        )
        trace_container.markdown(styled_text, unsafe_allow_html=True)
