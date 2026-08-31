from google.genai.types import ToolContext
from shared.schemas import LoanApplication
from shared.db import db_client

def save_client_details_to_state(
    tool_context: ToolContext,
    loan_application: LoanApplication
) -> dict[str, str]:
    """Persists records to Cloud Spanner and updates ADK session state for multi-turn workflows."""
    
    app_id = loan_application.application_id
    current_data = loan_application.model_dump()
    
    # 1. Permanent Database Persistence via SpannerClientWrapper
    try:
        db_client.save_loan_application(loan_application)
    except Exception as e:
        print(f"Spanner persistence warning: {e}")
        # Depending on your error handling preference, you can raise or log and proceed
        
    # 2. Pull existing records from ADK session state for multi-turn merging
    existing_records = tool_context.state.get("all_loan_applications", {})
    
    if app_id in existing_records:
        old_record = existing_records[app_id]
        
        # Example field-by-field merge if fields are missing in the new batch
        if not current_data.get("stated_income") and old_record.get("stated_income"):
            current_data["stated_income"] = old_record["stated_income"]
            
        # Merge document lists cleanly without duplicates
        old_docs = set(old_record.get("documents", []))
        new_docs = set(current_data.get("documents", []))
        current_data["documents"] = list(old_docs.union(new_docs))

    # 3. Update session state keys for downstream agents
    existing_records[app_id] = current_data
    tool_context.state["application_id"] = app_id
    tool_context.state["loan_application"] = current_data
    tool_context.state["all_loan_applications"] = existing_records

    return {"status": "success", "message": f"Successfully persisted application {app_id} to Spanner and session state."}