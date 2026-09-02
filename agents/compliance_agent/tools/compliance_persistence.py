from google.adk.tools import ToolContext
from shared.schemas import ComplianceResult
from shared.db import db_client
from shared.rate_limiter import handle_rate_limit

@handle_rate_limit
def persist_compliance_record(
    tool_context: ToolContext,
    application_id: str,
    aml_check_passed: bool,
    sanctions_clear: bool,
    audit_trail_id: str,
    regulatory_notes: str
) -> dict:
    """Persists the final regulatory compliance decision and immutable audit trail directly to Google Cloud Spanner."""
    
    result = ComplianceResult(
        application_id=application_id,
        aml_check_passed=aml_check_passed,
        sanctions_clear=sanctions_clear,
        audit_trail_id=audit_trail_id,
        regulatory_notes=regulatory_notes
    )

    try:
        db_client.save_compliance_result(result)
        db_status = "Successfully committed compliance record to Cloud Spanner."
    except Exception as e:
        db_status = f"Spanner compliance persistence failed: {e}"
        raise e

    # Update session state for downstream reporting or root router agents
    tool_context.state["compliance_result"] = result.model_dump()

    return {
        "status": db_status,
        "application_id": application_id,
        "persisted_compliance_data": result.model_dump()
    }