from typing import Optional
from google.adk.tools import ToolContext
from shared.schemas import IngestionResult, LoanApplication
from shared.db import db_client

def save_client_details_to_state(
    tool_context: ToolContext,
    ingestion_result: Optional[IngestionResult] = None,
    loan_application: Optional[LoanApplication] = None
) -> dict[str, str]:
    """Persists ingestion results and loan application records to Spanner and updates ADK session state."""
    
    # 1. Save ingestion/extraction telemetry if provided
    if ingestion_result:
        try:
            db_client.save_ingestion_result(ingestion_result)
        except Exception as e:
            print(f"Spanner ingestion persistence warning: {e}")
            
    # 2. Save core loan application record if provided
    if loan_application:
        try:
            db_client.save_loan_application(loan_application)
        except Exception as e:
            print(f"Spanner loan application persistence warning: {e}")

    # 3. Handle session state updates and merging for downstream agents
    app_id = (loan_application and loan_application.application_id) or \
             (ingestion_result and ingestion_result.application_id)
             
    if app_id:
        existing_records = tool_context.state.get("all_loan_applications", {})
        
        # Build current dictionary snapshot
        current_data = {}
        if loan_application:
            current_data.update(loan_application.model_dump())
        if ingestion_result:
            current_data.update(ingestion_result.model_dump())
            
        # Merge with previous state if multi-turn interaction
        if app_id in existing_records:
            old_record = existing_records[app_id]
            old_docs = set(old_record.get("documents", []))
            new_docs = set(current_data.get("documents", []))
            current_data["documents"] = list(old_docs.union(new_docs))
            
            # Keep older intake fields if new payload leaves them blank
            for field in ["applicant_name", "requested_amount", "employment_status", "stated_income"]:
                if not current_data.get(field) and old_record.get(field):
                    current_data[field] = old_record[field]

        existing_records[app_id] = current_data
        tool_context.state["application_id"] = app_id
        tool_context.state["loan_application"] = current_data
        tool_context.state["all_loan_applications"] = existing_records

    return {"status": "success", "message": f"Successfully processed records for application {app_id}."}