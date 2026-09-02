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
from agents.dispatcher_agent.tools.lending_package_persistence import finalize_and_record_application
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

# 2. Define the dedicated Lending Package Writer Agent
lending_package_writer_agent = Agent(
    name="LendingPackageWriter",
    model=MODELS.get("dispatch", "gemini-2.5-flash"),
    instruction="""
    You are the CrediSync Lending Package Writer. 
    1. **VERIFY STATE:** Review the active session state to ensure `ingestion_result`, `valuation_result`, `underwriting_result`, and `compliance_result` are fully populated.
    2. **DETERMINE VERDICT:** Synthesize the final evaluation results, risk notes, and policy checks to establish an `overall_status` (e.g., APPROVED, REJECTED, REVISE) and an executive `summary_notes`.
    3. **PERSIST RECORD:** Immediately call the `finalize_and_record_application` tool, passing the active `application_id`, the determined `overall_status`, and the `summary_notes` to commit the record to Cloud Spanner.
    """,
    tools=[finalize_and_record_application],
    output_key="final_lending_package"
)

# 3. Wrap everything into the master sequential orchestration pipeline
cred_sync_pipeline = SequentialAgent(
    name="CrediSync_Workflow",
    sub_agents=[
        ingestion_agent, 
        valuation_agent, 
        credit_review_pipeline, 
        lending_package_writer_agent
    ],
    description="Executes document ingestion, valuation, the iterative credit review loop, and final Spanner persistence via the writer agent."
)

# 4. Define your Dispatcher Agent (The Clean Gatekeeper)
cred_sync_dispatcher = Agent(
    name="CrediSyncDispatcher",
    model=MODELS.get("dispatch", "gemini-2.5-flash"),
    instruction="""
    You are the CrediSync Underwriting Dispatcher. 
    1. **GREETING:** Welcome the user professionally to CrediSync Underwriting.
    2. **AWAIT DOCUMENT UPLOADS:** Do NOT auto-initialize, fabricate, or generate fallback mock data. 
       Request and wait for the user to upload unstructured financial documents and application details.
    3. **STATE GATING:** Do not trigger the pipeline until the ingestion agent has successfully 
       parsed and saved client details to session state (`ingestion_result`).
    4. **PIPELINE EXECUTION:** Hand off control to the `CrediSync_Workflow`. 
    5. **FINAL REPORTING:** Once the workflow completes, present the finalized lending package verdict 
       and database persistence confirmation clearly and professionally to the user.
    
    TONE: Professional, authoritative, and compliance-focused.
    """,
    sub_agents=[cred_sync_pipeline],
)

# Root dispatcher entrypoint
root_agent = cred_sync_dispatcher