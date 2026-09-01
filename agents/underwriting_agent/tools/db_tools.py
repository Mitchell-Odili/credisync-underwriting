from google.adk.tools import ToolContext
from shared.schemas import UnderwritingResult
from shared.db import db_client

def persist_underwriting_record(
    tool_context: ToolContext,
    application_id: str,
    probability_of_default: float,
    recommended_limit: float,
    policy_rules_passed: bool,
    notes: str
) -> dict:
    """Persists the final underwriting decision and metrics directly to Google Cloud Spanner."""
    
    result = UnderwritingResult(
        application_id=application_id,
        probability_of_default=probability_of_default,
        recommended_limit=recommended_limit,
        policy_rules_passed=policy_rules_passed,
        notes=notes
    )

    try:
        db_client.save_underwriting_result(result)
        db_status = "Successfully committed to Cloud Spanner."
    except Exception as e:
        db_status = f"Spanner persistence failed: {e}"
        raise e

    # Update session state for downstream compliance agent
    tool_context.state["underwriting_result"] = result.model_dump()

    return {
        "status": db_status, 
        "application_id": application_id,
        "persisted_data": result.model_dump()
    }