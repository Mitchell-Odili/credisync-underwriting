from google.adk.models import GeminiModel

MODELS = {
    "dispatch": "gemini-3.5-flash-lite",
    "ingestion": "gemini-3.5-flash-lite",
    "valuation": "gemini-3.5-flash-lite",
    "underwriting": "gemini-3.5-flash-lite",
    "compliance": "gemini-3.5-flash-lite"
}

def get_model(service_name: str) -> GeminiModel:
    """Retrieves the GeminiModel instance mapped to a specific microservice."""
    model_name = MODELS.get(service_name, "gemini-3.5-flash-lite")
    return GeminiModel(model_name=model_name)