import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import LoopAgent
from agents.underwriting_agent.agent import underwriting_agent
from agents.compliance_agent.agent import compliance_agent
from agents.risk_critic_agent.agent import risk_critic_agent
from shared.config import MODELS


# Wrap the full multi-agent sequence in an iterative LoopAgent
credit_review_pipeline = LoopAgent(
    name="CreditReviewPipeline",
    description="Iteratively evaluates, critiques, and refines loan underwriting, compliance checks, and risk thresholds.",
    sub_agents=[
        underwriting_agent,
        compliance_agent,
        risk_critic_agent
    ],
    max_iterations=3,  # Caps the refinement cycles to prevent infinite loops
    output_key="lending_package",  # Maps the final synthesized output directly to your state key"  
)

root_agent = credit_review_pipeline