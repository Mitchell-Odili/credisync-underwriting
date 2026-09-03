import os
import logging
from google.cloud import modelarmor_v1
from google.api_core import client_options

logger = logging.getLogger(f"credisync.{__name__}")

def create_model_armor_callbacks(project_id: str, region: str, template_id: str):
    """
    Factory creating ADK-compliant before_model_callback and after_model_callback
    integrated with Google Cloud Model Armor.
    """
    # Crucial: Model Armor requires routing to the specific regional endpoint
    api_endpoint = f"modelarmor.{region}.rep.googleapis.com"
    opts = client_options.ClientOptions(api_endpoint=api_endpoint)
    client = modelarmor_v1.ModelArmorClient(client_options=opts)
    
    template_name = f"projects/{project_id}/locations/{region}/templates/{template_id}"

    def before_model_callback(*args, callback_context=None, **kwargs):
        """Inspects user prompt at the model boundary using Model Armor."""
        # Flexibly absorb arguments sent by different ADK runtime versions
        ctx = callback_context or (args[0] if args else None)
        
        # Extract prompt text safely from context
        prompt_text = ""
        if ctx:
            prompt_text = getattr(ctx, "prompt", "") or kwargs.get("prompt", "")
            if not prompt_text and hasattr(ctx, "model_request"):
                prompt_text = getattr(ctx.model_request, "contents", "")
        
        # If there's no text string to check right now, let it pass through
        if not prompt_text:
            return None

        try:
            request = modelarmor_v1.SanitizeUserPromptRequest(
                name=template_name,
                user_prompt_data=modelarmor_v1.DataItem(text=str(prompt_text))
            )
            response = client.sanitize_user_prompt(request=request)
            result = response.sanitization_result
            
            # Check if Model Armor detected a violation (Prompt Injection / Jailbreak)
            if result and result.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
                logger.warning(f"Security Alert: Model Armor blocked malicious payload. Result: {result}")
                raise ValueError(f"Security Policy Violation: Blocked by Model Armor template '{template_id}'.")
                
        except Exception as e:
            if isinstance(e, ValueError):
                raise e  # Propagate the security block upwards
            logger.error(f"Model Armor API error during inspection: {e}")
            # Fail open or closed depending on preference (currently passes through on infrastructure errors)
        
        return None

    def after_model_callback(*args, callback_context=None, **kwargs):
        """Optional model response inspection hook for outbound safety or PII checks."""
        return None

    return before_model_callback, after_model_callback