import sys
import pathlib

root_dir = pathlib.Path(__file__).parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset

from shared.config import MODELS
from agents.valuation_agent.tools.valuation_tool import assess_and_save_borrower_valuation

# Load the structured skill directory
skill_dir = pathlib.Path(__file__).parent / "skills" / "valuation-extractor"
valuation_extractor_skill = load_skill_from_dir(skill_dir)

# Wrap the local skill in a SkillToolset
valuation_extractor_toolset = SkillToolset(skills=[valuation_extractor_skill])

valuation_agent = Agent(
    model=MODELS.get("valuation", "gemini-2.5-flash"),
    name="ValuationAgent",
    instruction=(
        "You are the Valuation Agent for CrediSync. Your role is to assess borrower solvency, "
        "query credit risk profiles, and evaluate collateral-to-loan ratios using your unified valuation tool."
    ),
    tools=[
        assess_and_save_borrower_valuation, 
        valuation_extractor_toolset
    ],
     output_key="val_result", # Automatically captures and saves the final output to session state
)

root_agent = valuation_agent