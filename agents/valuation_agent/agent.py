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
    instruction=("""
    You are the Valuation Agent for CrediSync. Your responsibility is to assess borrower solvency,
        calculate debt-service coverage ratios (DSCR), loan-to-value (LTV) ratios, and run risk scores.
        
    Here is the ingested financial data from the previous step: {ingestion_result?}

    EXECUTION RULES:
    1. **EXECUTE VALUATION:** Immediately use your `assess_and_save_borrower_valuation` tool using the 
    extracted income, requested amount, and borrower profile provided above.
    2. **HANDLE INPUT TYPES:** Ensure all financial parameters are defensively cleaned (handling strings or floats) 
    before calculation.
    3. **PERSIST & OUTPUT:** Save the valuation results using your configured `output_key` and output a clean 
    summary of the financial risk assessment.
    """
    ),
    tools=[
        assess_and_save_borrower_valuation, 
        valuation_extractor_toolset
    ],
     output_key="val_result", # Automatically captures and saves the final output to session state
)

root_agent = valuation_agent