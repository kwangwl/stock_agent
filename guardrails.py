import pandas as pd
import streamlit as st


def add_result(results, category, details):
    status = "⚠️ Blocked" if details else "✅ 통과"
    details_str = ", ".join(details) if details else "-"

    results.append({
        "Category": category,
        "Test result": status,
        "Details": details_str
    })


def display_guardrail_result_table(trace_container, assessment):
    """
    가드레일 결과를 테이블 형태로 표시하는 함수
    """
    results = []

    # Word Policy 검사
    if 'wordPolicy' in assessment:
        details = []
        for word in assessment['wordPolicy'].get('customWords', []):
            if word.get('action') == 'BLOCKED':
                details.append(f"Detected '{word['match']}' word")
        add_result(results, "Word filters", details)

    # Sensitive Information Policy 검사
    if 'sensitiveInformationPolicy' in assessment:
        details = []
        for regex in assessment['sensitiveInformationPolicy'].get('regexes', []):
            if regex.get('action') == 'BLOCKED':
                details.append(f"Detected regex pattern '{regex['name']}'")

        for pii in assessment['sensitiveInformationPolicy'].get('piiEntities', []):
            if pii.get('action') in ['BLOCKED', 'ANONYMIZED']:
                details.append(f"Detected {pii['type']}")

        add_result(results, "Sensitive information filters", details)

    # Content Policy 검사
    if 'contentPolicy' in assessment:
        details = []
        for filter in assessment['contentPolicy'].get('filters', []):
            if filter.get('action') == 'BLOCKED':
                details.append(f"Detected {filter['type']} content")

        add_result(results, "Content filters", details)

    # Topic Policy 검사
    if 'topicPolicy' in assessment:
        details = []
        for topic in assessment['topicPolicy'].get('topics', []):
            if topic.get('action') == 'BLOCKED':
                details.append(f"Detected {topic['name']} topic")

        add_result(results, "Topic filters", details)

    # Contextual Grounding Policy 검사
    if 'contextualGroundingPolicy' in assessment:
        details = []
        for filter in assessment['contextualGroundingPolicy'].get('filters', []):
            if filter.get('action') == 'BLOCKED':
                details.append(f"Failed {filter['type']} check")

        add_result(results, "Contextual grounding filters", details)

    if results:
        df = pd.DataFrame(results)
        trace_container.dataframe(df, hide_index=True, use_container_width=True)


def display_guardrail_trace(trace_container, guardrail_trace):
    """
    가드레일 트레이스 정보를 표시하는 메인 함수
    """
    action = guardrail_trace.get('action')

    if 'inputAssessments' in guardrail_trace:
        with trace_container.chat_message("ai"):
            st.markdown("Bedrock Guardrails 검사 수행 (입력)")

        if action == "NONE":
            trace_container.success("✅ 통과")

        if action == "INTERVENED":
            trace_container.warning("⚠️ 제한 발생")
            for assessment in guardrail_trace.get('inputAssessments', []):
                display_guardrail_result_table(trace_container, assessment)

    else:
        # 'outputAssessments' in guardrail_trace:
        with trace_container.chat_message("ai"):
            st.markdown("Bedrock Guardrails 검사 수행 (출력)")

        if action == "NONE":
            trace_container.success("✅ 통과")

        if action == "INTERVENED":
            trace_container.warning("⚠️ 제한 발생")
            for assessment in guardrail_trace.get('outputAssessments', []):
                display_guardrail_result_table(trace_container, assessment)
