import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from shared.config import MODELS
from shared.logging_callback import before_agent_callback, after_agent_callback

# 1. Import your database persistence tool from the tools folder
from agents.underwriting_agent.tools.db_tools import persist_underwriting_record

# 2. Load the credit-policy skill directory (which includes policy_logic.py & SKILL.md)
skill_dir = pathlib.Path(__file__).parent / "skills" / "credit-policy"
credit_policy_skill = load_skill_from_dir(skill_dir)
credit_policy_toolset = SkillToolset(skills=[credit_policy_skill])

# 3. Underwriting Agent Definition
underwriting_agent = Agent(
    name="UnderwritingAgent",
    model=MODELS.get("underwriting", "gemini-2.5-flash"),
    description="Evaluates valuation telemetry against institutional credit policies and persists decisions.",
    instruction="""
    You are the Senior Underwriter for CrediSync.
    
    Review the current loan valuation telemetry:
    - VALUATION DATA: {val_result?}
    
    If prior risk feedback exists from the review loop, incorporate it:
    - PRIOR RISK FEEDBACK: {risk_feedback?}
    
   Generate or refine the underwriting structure, pricing terms, and risk score.
    """,
    # Both tools are passed together in the toolset array
    tools=[credit_policy_toolset, persist_underwriting_record],
    # Wire the lifecycle hooks
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    output_key="underwriting_result"
)

root_agent = underwriting_agent