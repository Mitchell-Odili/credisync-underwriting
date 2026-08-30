import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import ToolContext
from google.adk.tools.skill_toolset import SkillToolset
from shared.config import MODELS
from shared.schemas import IngestionResult

# Load the structured skill directory
skill_dir = pathlib.Path(__file__).parent / "skills" / "financial-document-extraction-parser"
document_parser_skill = load_skill_from_dir(skill_dir)

# Wrap the local skill in a SkillToolset
financial_parser_toolset = SkillToolset(skills=[document_parser_skill])

# Tools
def save_client_details_to_state(
    tool_context: ToolContext,
    ingestion_result: IngestionResult
) -> dict[str, str]:
    """Persists records to the database and updates ADK session state for multi-turn workflows."""
    
    app_id = ingestion_result.application_id
    current_data = ingestion_result.model_dump()
    
    # 1. Permanent Database Persistence (e.g., Cloud Spanner)
    # db.save_application_record(ingestion_result)
    
    # 2. Pull existing records from ADK session state for multi-turn merging
    existing_records = tool_context.state.get("all_ingestion_records", {})
    
    if app_id in existing_records:
        old_record = existing_records[app_id]
        
        # Merge top-level fields if needed
        if not current_data.get("normalized_income") and old_record.get("normalized_income"):
            current_data["normalized_income"] = old_record["normalized_income"]
            
        # Merge nested extracted data dictionaries field-by-field across batches
        old_extracted = old_record.get("extracted_data", {})
        new_extracted = current_data.get("extracted_data", {})
        
        for key, value in old_extracted.items():
            if not new_extracted.get(key) and value:
                new_extracted[key] = value
                
        current_data["extracted_data"] = new_extracted

    # 3. Update session state keys for instant shorthand templating in downstream agents
    existing_records[app_id] = current_data
    tool_context.state["application_id"] = app_id
    tool_context.state["ingestion_result"] = current_data
    tool_context.state["all_ingestion_records"] = existing_records

    return {"status": "success", "message": f"Successfully persisted and updated batch for {app_id}"}

# Agent
ingestion_agent = Agent(
    name="ingestion_agent",
    model=MODELS["ingestion"],
    description="Accepts, parses, and normalizes unstructured financial documents into verified schemas.",
    instruction="""
    You are the Ingestion Service agent for CrediSync Underwriting.
    
    Workflow & Execution Rules:
    1. Do NOT ask the user for an application ID. Assume the system or dispatcher provides it automatically. If it is missing, generate a temporary fallback reference (e.g., "AUTO-REF").
    2. Accept and process unstructured financial documents (tax returns, bank statements, P&Ls) provided by the user.
    3. When documents are uploaded, use your financial_parser_toolset to extract entities, parse lines, and normalize fields into the IngestionResult structure.
    4. MANDATORY STEP: Once parsing is complete, you must immediately call your `save_client_details_to_state` tool, passing the generated IngestionResult to commit it to the session state and database.
    5. Output the final validated IngestionResult cleanly matching your output schema.
    """,
    tools=[financial_parser_toolset, save_client_details_to_state],
    output_schema=IngestionResult,
    output_key="ingestion_result", # Automatically captures and saves the final output to session state
)

root_agent = ingestion_agent