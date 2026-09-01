import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from shared.config import MODELS

# 1. Import your database persistence tool from the tools folder
from agents.underwriting_agent.tools.db_tools import persist_underwriting_record

# 2. Load the credit-policy skill directory (which includes policy_logic.py & SKILL.md)
skill_dir = pathlib.Path(__file__).parent / "skills" / "credit-policy"
credit_policy_skill = load_skill_from_dir(skill_dir)
credit_policy_toolset = SkillToolset(skills=[credit_policy_skill])

# 3. Underwriter Agent Definition
underwriter_agent = Agent(
    name="UnderwriterAgent",
    model=MODELS["underwriting"],
    description="Evaluates valuation telemetry against institutional credit policies and persists decisions.",
    instruction="""
    You are the Senior Credit Underwriter Agent for CrediSync.
    
    UPSTREAM TELEMETRY:
    - Valuation Metrics: {val_result?}
    
    WORKFLOW:
    1. Read the upstream valuation telemetry above.
    2. Use your `assess_credit` skill function to run policy compliance checks and compute risk/limits.
    3. Call `persist_underwriting_record` to commit the results to Google Cloud Spanner and update session state.
    4. Output your final underwriting memo summary.
    """,
    # Both tools are passed together in the toolset array
    tools=[credit_policy_toolset, persist_underwriting_record],
    output_key="underwriting_result"
)

root_agent = underwriter_agent