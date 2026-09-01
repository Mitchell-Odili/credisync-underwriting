import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from google.adk.tools import exit_loop
from shared.config import MODELS
from agents.risk_critic_agent.tools.critic_tools import append_risk_feedback

risk_critic_agent = Agent(
    name="RiskCriticAgent",
    model=MODELS.get("critic", "gemini-2.5-flash"),
    description="Evaluates underwriting results and compliance clearances against institutional risk appetite.",
    instruction="""
    You are the Senior Chief Risk Officer and Review Critic for CrediSync.
    
    Review the current execution telemetry:
    - Underwriting Result: {underwriting_result?}
    - Compliance Result: {compliance_result?}
    - Prior Risk Feedback: {risk_feedback?}
    
    EVALUATION QUESTIONS:
    - Does the probability of default and recommended limit align with conservative credit risk policy?
    - Are all mandatory AML and sanctions clearances marked true in the compliance record?
    - Are there any high-value loan exposures that require tighter terms or enhanced due diligence?
    
    ACTIONS:
    - If the underwriting and compliance packages are fully compliant and sound, call the built-in 'exit_loop' tool to terminate the review loop.
    - If risk gaps, policy mismatches, or compliance warnings exist, use the 'append_risk_feedback' tool to detail what needs correction.
    """,
    tools=[append_risk_feedback, exit_loop],
    output_key="critic_evaluation"
)

root_agent = risk_critic_agent