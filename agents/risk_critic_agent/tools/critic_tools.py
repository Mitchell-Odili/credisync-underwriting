from google.adk.tools import ToolContext

def append_risk_feedback(tool_context: ToolContext, feedback_notes: str) -> dict:
    """Appends critical risk or compliance feedback to the session state for the underwriting agent to revise."""
    tool_context.state["risk_feedback"] = feedback_notes
    return {"status": "Feedback recorded", "risk_feedback": feedback_notes}