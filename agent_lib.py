import boto3
import os


def get_agent_response(session_id, prompt):
    """Get a response from the Bedrock agent using specified parameters."""

    # Create a Boto3 client for the Bedrock Runtime service
    session = boto3.Session()
    bedrock_agent = session.client(service_name='bedrock-agent-runtime', region_name=os.environ.get("BWB_REGION_NAME"))

    # Invoke the Bedrock agent with the specified parameters
    response = bedrock_agent.invoke_agent(
        agentId=os.environ.get("BWB_AGENT_ID"),
        agentAliasId=os.environ.get("BWB_AGENT_ALIAS_ID"),
        enableTrace=True,
        sessionId=session_id,
        inputText=prompt,
    )

    # Initialize variables to store the output, citations, and trace information
    output_text = ""
    trace = {}

    # Process each event in the response
    for event in response.get("completion"):
        # Combine the chunks to get the output text
        if "chunk" in event:
            chunk = event["chunk"]
            output_text += chunk["bytes"].decode()

        # Extract trace information from all events
        if "trace" in event:
            if "orchestrationTrace" in event["trace"]["trace"]:
                if "orchestrationTrace" not in trace:
                    trace["orchestrationTrace"] = []
                trace["orchestrationTrace"].append(event["trace"]["trace"]["orchestrationTrace"])

    # Return the processed output, citations, and trace information
    return {
        "output_text": output_text,
        "trace": trace
    }
