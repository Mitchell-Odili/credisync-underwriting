import os
from dotenv import load_dotenv

# Load .env 
load_dotenv()

# Note: All agents, including security-boundary entry/exit points, 
# successfully utilize gemini-3.5-flash-lite via the global endpoint.

MODELS = {
    # Entry and security-boundary points 

    "dispatch": "gemini-3.5-flash-lite",
    "ingestion": "gemini-3.5-flash-lite",
    
    # Internal deep-processing agents
    "valuation": "gemini-3.5-flash-lite",
    "underwriting": "gemini-3.5-flash-lite",
    "compliance": "gemini-3.5-flash-lite",
    "critic": "gemini-3.5-flash-lite",
    
    # Exit / reporting point
    "lending": "gemini-3.5-flash-lite"
}