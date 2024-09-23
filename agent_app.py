import streamlit as st
import agent_lib as glib
import pandas as pd
import uuid
import json


AGENT_ID = st.secrets["AGENT_ID"]
ALIAS_ID = {
    "Sonnet 3.5": st.secrets["ALIAS_ID_3_5"],
    "Sonnet 3.0": st.secrets["ALIAS_ID_3"],
}


# function
def display_stock_chart(trace_container, trace):
    chart_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    chart = json.loads(chart_text)

    df = pd.DataFrame(list(chart.items()), columns=['Date', 'Closing Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # st.markdown("**주식 차트**")
    trace_container.line_chart(df, x_label="날짜", y_label="종가")


def display_stock_balance(trace_container, trace):
    balance_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    balance = json.loads(balance_text)

    df = pd.DataFrame.from_dict(balance, orient='index').transpose()

    trace_container.dataframe(df, use_container_width=True)


def display_recommendations(trace_container, trace):
    recommendations_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    recommendations = json.loads(recommendations_text)

    df = pd.DataFrame.from_dict(recommendations, orient='index').transpose()

    trace_container.dataframe(df, use_container_width=True)


# main page
st.set_page_config(page_title="Stock Analyzer")
st.title("Bedrock Agent 주식 분석")

selected_option = st.sidebar.radio(
    "FM 모델을 선택하세요:",
    ('Sonnet 3.5', 'Sonnet 3.0')
)

input_text = st.text_input("종목명을 입력하세요  (한글 이름 or 영어 이름 or 야후 파이낸스 ticker 입력 가능)")
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
                trace = event["trace"]["trace"]["orchestrationTrace"]

                if "rationale" in trace:
                    with trace_container.chat_message("ai"):
                        st.markdown(trace['rationale']['text'])

                elif function_name != "":
                    if function_name == "get_stock_chart":
                        # print("asdf")
                        display_stock_chart(trace_container, trace)

                    elif function_name == "get_stock_balance":
                        # print("asdf")
                        display_stock_balance(trace_container, trace)

                    elif function_name == "get_recommendations":
                        # print("asdf")
                        display_recommendations(trace_container, trace)

                    function_name = ""

                else:
                    function_name = trace.get('invocationInput', {}).get('actionGroupInvocationInput', {}).get(
                        'function', "")

                # trace_container.json(event["trace"]["trace"])

        # 응답 출력
        trace_container.divider()
        trace_container.subheader("Analysis Report")
        trace_container.write(output_text)
