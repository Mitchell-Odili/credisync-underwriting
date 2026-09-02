from google.adk.tools import ToolContext
from shared.schemas import LendingPackage
from shared.db import db_client
from shared.rate_limiter import handle_rate_limit

@handle_rate_limit
def finalize_and_record_application(
    tool_context: ToolContext,
    application_id: str,
    overall_status: str,
    summary_notes: str
) -> dict:
    """Persists the final LendingPackage decision and summary directly to Google Cloud Spanner."""
    
    package = LendingPackage(
        application_id=application_id,
        overall_status=overall_status,
        summary_notes=summary_notes
    )

    try:
        db_client.save_lending_package(package)
        db_status = "Successfully committed to Cloud Spanner."
    except Exception as e:
        db_status = f"Spanner persistence failed: {e}"
        raise e

    # Update session state for final reporting and tracking
    tool_context.state["final_lending_package"] = package.model_dump()

    return {
        "status": db_status, 
        "application_id": application_id,
        "persisted_data": package.model_dump()
    }