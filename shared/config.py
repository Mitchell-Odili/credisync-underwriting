import os
from dotenv import load_dotenv

# Load .env 
load_dotenv()

MODELS = {
    "dispatch": "gemini-3.5-flash-lite",
    "ingestion": "gemini-3.5-flash-lite",
    "valuation": "gemini-3.5-flash-lite",
    "underwriting": "gemini-3.5-flash-lite",
    "compliance": "gemini-3.5-flash-lite"
}
