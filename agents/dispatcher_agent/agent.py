import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent, SequentialAgent, LoopAgent
from agents.ingestion_agent.agent import ingestion_agent
from agents.valuation_agent.agent import valuation_agent
from agents.underwriting_agent.agent import underwriting_agent
from agents.compliance_agent.agent import compliance_agent
from agents.risk_critic_agent.agent import risk_critic_agent
from shared.config import MODELS

# 1. Define the iterative review loop directly
credit_review_pipeline = LoopAgent(
    name="CreditReviewPipeline",
    description="Iteratively evaluates, critiques, and refines loan underwriting, compliance checks, and risk thresholds.",
    sub_agents=[
        underwriting_agent,
        compliance_agent,
        risk_critic_agent
    ],
    max_iterations=3
)

# 2. Wrap everything into the master sequential orchestration pipeline
cred_sync_pipeline = SequentialAgent(
    name="CrediSync_Workflow",
    sub_agents=[ingestion_agent, valuation_agent, credit_review_pipeline],
    description="Executes sequential document ingestion, valuation, and the iterative credit review loop (underwriting, risk critic, compliance)."
)

# 2. Define your Dispatcher Agent (The Intelligent Gatekeeper)
cred_sync_dispatcher = Agent(
    name="CrediSyncDispatcher",
    model=MODELS.get("dispatch", "gemini-2.5-flash"),
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
    5. **REPORTING & PERSISTENCE:** Present the finalized lending package verdict clearly to the user once committed to Cloud Spanner.
    
    TONE: Professional, authoritative, and compliance-focused.
    """,
    sub_agents=[cred_sync_pipeline], # The sequential pipeline acts as a specialized sub-agent
    output_key="final_lending_package",
)

# Root dispatcher entrypoint
root_agent = cred_sync_dispatcher