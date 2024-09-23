import streamlit as st
import agent_lib as glib
import pandas as pd
import uuid
import json

AGENT_ID = st.secrets["AGENT_ID"]
ALIAS_ID = {
    "Sonnet 3.0": st.secrets["ALIAS_ID_3"],
    "Sonnet 3.5": st.secrets["ALIAS_ID_3_5"],
}


# function
def display_stock_chart(trace):
    chart_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    chart = json.loads(chart_text)

    df = pd.DataFrame(list(chart.items()), columns=['Date', 'Closing Price'])
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    st.markdown("**주식 차트**")
    st.line_chart(df, x_label="날짜", y_label="종가")


def display_stock_balance(trace):
    balance_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    balance = json.loads(balance_text)

    df = pd.DataFrame.from_dict(balance, orient='index').transpose()

    st.markdown("**재무 제표**")
    st.dataframe(df, use_container_width=True)


def display_recommendations(trace):
    recommendations_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    recommendations = json.loads(recommendations_text)

    df = pd.DataFrame.from_dict(recommendations, orient='index').transpose()

    st.markdown("**애널리스트 추천**")
    st.dataframe(df, use_container_width=True)


# main page
st.set_page_config(page_title="주식 분석 에이전트")
st.title("주식 분석 에이전트")

# sidebar (model id)

selected_option = st.sidebar.radio(
    "FM 모델을 선택하세요:",
    ('Sonnet 3.0', 'Sonnet 3.5')
)

input_text = st.text_area("종목명을 입력하세요  (한글 이름 or 영어 이름 or 야후 파이낸스 ticker 입력 가능)")
submit_button = st.button("분석 시작", type="primary")

if submit_button and input_text:
    with st.spinner("응답 생성 중..."):
        # 에이전트 호출 (세션은 항상 초기화 하도록 구성)
        response = glib.get_agent_response(
            AGENT_ID,
            ALIAS_ID[selected_option],
            str(uuid.uuid4()),
            input_text
        )

        # 응답 출력
        output_text = response["output_text"]
        st.subheader("분석 결과")
        st.write(output_text)

        # 추적 정보 표시
        st.divider()
        st.subheader("추론 기록")

        if response["trace"] and "orchestrationTrace" in response["trace"]:
            traces = response["trace"]["orchestrationTrace"]
            for index, item in enumerate(traces):
                function_name = item.get('invocationInput', {}).get('actionGroupInvocationInput', {}).get(
                    'function', "")

                if function_name == "get_stock_chart":
                    display_stock_chart(traces[index + 1])

                elif function_name == "get_stock_balance":
                    display_stock_balance(traces[index + 1])

                elif function_name == "get_recommendations":
                    display_recommendations(traces[index + 1])
