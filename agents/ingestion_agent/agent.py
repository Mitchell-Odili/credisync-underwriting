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