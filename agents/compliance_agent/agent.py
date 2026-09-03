import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from shared.config import MODELS
from agents.compliance_agent.tools.compliance_persistence import persist_compliance_record
from shared.logging_callback import before_agent_callback, after_agent_callback


# Load the regulatory-compliance skill directory
skill_dir = pathlib.Path(__file__).parent / "skills" / "regulatory-compliance"
compliance_skill = load_skill_from_dir(skill_dir)
compliance_toolset = SkillToolset(skills=[compliance_skill])

compliance_agent = Agent(
    name="ComplianceAgent",
    model=MODELS.get("compliance", "gemini-2.5-flash"),
    description="Validates underwriting decisions against regulatory frameworks, executes AML and sanctions checks, and persists audit records to Cloud Spanner.",
    instruction="""
    You are the Senior Compliance and Regulatory Agent for CrediSync.
    
    UPSTREAM TELEMETRY:
    - Underwriting Result: {underwriting_result?}
    
    MANDATORY WORKFLOW:
    1. Extract the `application_id`, `policy_rules_passed`, and `recommended_limit` from the upstream underwriting result.
    2. CALL your `evaluate_regulatory_compliance` skill function to perform statutory, AML, and sanctions validations.
    3. CALL the `persist_compliance_record` tool with the resulting data to securely commit the audit trail and compliance status to Google Cloud Spanner.
    4. Summarize the final compliance clearance status and audit reference ID for the execution record.
    """,
    tools=[compliance_toolset, persist_compliance_record],
    # Wire the lifecycle hooks
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    output_key="compliance_result"
)

root_agent = compliance_agent