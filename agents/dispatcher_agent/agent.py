import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent, SequentialAgent
from agents.ingestion_agent.agent import ingestion_agent
from agents.valuation_agent.agent import valuation_agent
from shared.config import MODELS

# 1. Define the deterministic pipeline of workers
cred_sync_pipeline = SequentialAgent(
    name="CrediSync_Workflow",
    sub_agents=[ingestion_agent, valuation_agent],
    description="Sequentially executes document ingestion and financial valuation for loan applications."
)

# 2. Define your Dispatcher Agent (The Intelligent Gatekeeper)
cred_sync_dispatcher = Agent(
    name="CrediSyncDispatcher",
    model=MODELS["dispatch"],
    instruction="""
    You are the CrediSync Underwriting Dispatcher. 
    1. **GREETING:** Welcome the user professionally to CrediSync Underwriting.
    2. **AWAIT DOCUMENT UPLOADS:** Do NOT auto-initialize, fabricate, or generate fallback mock data. 
    You MUST request and wait for the user to upload unstructured financial documents (tax returns,
     bank statements, P&Ls) and application details.
    3. **STATE GATING:** Do not trigger the pipeline until the ingestion agent has successfully 
    parsed and saved the client details to session state (`ingestion_result`).
    4. **PIPELINE EXECUTION:** Once documents are ingested and state is saved, hand off control 
    to the `CrediSync_Workflow`.
    5. **REPORTING:** Present the final valuation verdict (`val_result`) clearly to the user.
    
    TONE: Professional, authoritative, and compliance-focused.
    """,
    sub_agents=[cred_sync_pipeline], # The sequential pipeline acts as a specialized sub-agent
    output_key="val_result"
)

# Root dispatcher entrypoint
root_agent = cred_sync_dispatcher