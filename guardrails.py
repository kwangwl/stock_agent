import pandas as pd


def add_result(results, category, action, details=""):
    status = "✅ 통과" if action == "NONE" else "⚠️ Blocked"
    results.append({
        "Category": category,
        "Test result": status,
        "Details": details
    })


def display_guardrail_result_table(trace_container, assessment, assessment_type="입력"):
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
        add_result(results, "Word filters",
                   "BLOCKED" if details else "NONE",
                   ", ".join(details) if details else "-")

    # Sensitive Information Policy 검사
    if 'sensitiveInformationPolicy' in assessment:
        details = []
        for regex in assessment['sensitiveInformationPolicy'].get('regexes', []):
            if regex.get('action') == 'BLOCKED':
                details.append(f"Detected regex pattern '{regex['name']}'")

        for pii in assessment['sensitiveInformationPolicy'].get('piiEntities', []):
            if pii.get('action') in ['BLOCKED', 'ANONYMIZED']:
                details.append(f"Detected {pii['type']}")
        add_result("Sensitive information filters",
                   "BLOCKED" if details else "NONE",
                   ", ".join(details) if details else "-")

    # Content Policy 검사
    if 'contentPolicy' in assessment:
        details = []
        for filter in assessment['contentPolicy'].get('filters', []):
            if filter.get('action') == 'BLOCKED':
                details.append(f"Detected {filter['type']} content")
        add_result("Content filters",
                   "BLOCKED" if details else "NONE",
                   ", ".join(details) if details else "-")

    # Topic Policy 검사
    if 'topicPolicy' in assessment:
        details = []
        for topic in assessment['topicPolicy'].get('topics', []):
            if topic.get('action') == 'BLOCKED':
                details.append(f"Detected {topic['name']} topic")
        add_result("Topic filters",
                   "BLOCKED" if details else "NONE",
                   ", ".join(details) if details else "-")

    # Contextual Grounding Policy 검사
    if 'contextualGroundingPolicy' in assessment:
        details = []
        for filter in assessment['contextualGroundingPolicy'].get('filters', []):
            if filter.get('action') == 'BLOCKED':
                details.append(f"Failed {filter['type']} check")
        add_result("Contextual grounding filters",
                   "BLOCKED" if details else "NONE",
                   ", ".join(details) if details else "-")

    if results:
        trace_container.markdown(f"### {assessment_type} 평가 결과")
        df = pd.DataFrame(results)
        trace_container.dataframe(df, hide_index=True, use_container_width=True)


def display_guardrail_trace(trace_container, guardrail_trace):
    """
    가드레일 트레이스 정보를 표시하는 메인 함수
    """
    action = guardrail_trace.get('action')

    if action == "NONE":
        trace_container.success("✅ 가드레일 검사 통과")
        return

    if action == "INTERVENED":
        trace_container.warning("⚠️ 가드레일 제한 발생")

        # 입력 평가 처리
        for assessment in guardrail_trace.get('inputAssessments', []):
            display_guardrail_result_table(trace_container, assessment, "입력")

        # 출력 평가 처리
        for assessment in guardrail_trace.get('outputAssessments', []):
            display_guardrail_result_table(trace_container, assessment, "출력")