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
from agents.ingestion_agent.tools.persistence import save_client_details_to_state

# Load the structured skill directory
skill_dir = pathlib.Path(__file__).parent / "skills" / "financial-document-extraction-parser"
document_parser_skill = load_skill_from_dir(skill_dir)

# Wrap the local skill in a SkillToolset
financial_parser_toolset = SkillToolset(skills=[document_parser_skill])

# Agent
ingestion_agent = Agent(
    name="ingestion_agent",
    model=MODELS.get("ingestion", "gemini-2.5-flash"),
    description="Accepts, parses, and normalizes unstructured financial documents into verified schemas.",
    instruction="""
    You are the Ingestion Service agent for CrediSync Underwriting.
    
    Workflow & Execution Rules:
    1. **AWAIT DOCUMENT UPLOADS:** Do NOT auto-initialize, fabricate, or generate fallback mock data (such as "AUTO-REF") if no files or documents have been provided. Wait for the user or upstream system to upload unstructured financial documents (tax returns, bank statements, P&Ls) before proceeding.
    2. **Process Uploaded Files:** Once financial documents are provided by the user, use your financial extraction and parsing tools to process the data and normalize fields into the correct schema.
    3. **MANDATORY PERSISTENCE:** Once parsing is complete, you must immediately call your `save_client_details_to_state` tool, passing the extracted data to commit it to Google Cloud Spanner and session state.
    4. **Clean Output:** Output the final validated application record clearly.
    """,
    tools=[financial_parser_toolset, save_client_details_to_state],
    # output_schema=IngestionResult,
    output_key="ingestion_result", # Automatically captures and saves the final output to session state
)

root_agent = ingestion_agent