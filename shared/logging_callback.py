import logging
import time
from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(f"credisync.{__name__}")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '{"severity": "%(levelname)s", "time": "%(asctime)s", "logger": "%(name)s", "message": "%(message)s", "extra": %(extra_data)s}'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Global store for timing per invocation/session if needed, 
# or you can store start time directly on the context/state.
_timing_store = {}

def before_agent_callback(callback_context: CallbackContext) -> None:
    agent_name = callback_context.agent_name  
    _timing_store[callback_context.invocation_id] = time.time()
    
    # Safely extract state keys without assuming .keys() exists
    state_keys = []
    try:
        state = getattr(callback_context, "state", None)
        if state is not None:
            if hasattr(state, "keys"):
                state_keys = list(state.keys())
            elif isinstance(state, dict):
                state_keys = list(state.keys())
            elif hasattr(state, "__dict__"):
                state_keys = list(state.__dict__.keys())
    except Exception:
        state_keys = []

    logger.info(
        f"Agent '{agent_name}' execution started.",
        extra={
            "extra_data": {
                "agent_name": agent_name,
                "phase": "before_agent",
                "invocation_id": callback_context.invocation_id,
                "state_keys": state_keys
            }
        }
    )

def after_agent_callback(callback_context: CallbackContext) -> None:
    agent_name = callback_context.agent_name  # Dynamically grabbed from ADK!
    start_time = _timing_store.pop(callback_context.invocation_id, time.time())
    duration = time.time() - start_time
    
    logger.info(
        f"Agent '{agent_name}' execution finished.",
        extra={
            "extra_data": {
                "agent_name": agent_name,
                "phase": "after_agent",
                "invocation_id": callback_context.invocation_id,
                "duration_seconds": round(duration, 3)
            }
        }
    )