import sys
import pathlib

# Resolve path to project root (two levels up from agents/ingestion_agent/)
root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from shared.config import get_model

# Ingestion Agent definition using the shared configuration lookup
ingestion_agent = Agent(
    name="ingestion_agent",
    model=get_model("ingestion"),
    description=(
        "Accepts and parses unstructured financial documents uploaded by loan applicants, "
        "such as tax returns and bank statements, with built-in validation and data extraction."
    ),
    instruction="""
    You are the Ingestion Service agent for CrediSync Underwriting.
    Your core responsibilities are:
    1. Accept incoming raw loan application payloads, tax returns, and bank statements from external interfaces (REST/SFTP).
    2. Sanitize inputs and check for malformed structures or missing required fields.
    3. Extract standardized entities (e.g., legal entity name, tax ID, stated annual revenue, liabilities).
    4. Format the extracted payload into a clean JSON data contract ready for hand-off to the Dispatcher and downstream risk evaluation agents.
    """,
)

# Export root agent for ADK discovery
root_agent = ingestion_agent