import time
import logging
from shared.logging_callback import before_agent_callback, after_agent_callback

# Robust mock to simulate the ADK CallbackContext with dynamic fields
class MockCallbackContext:
    def __init__(self, agent_name: str, invocation_id: str, state: dict):
        self.agent_name = agent_name
        self.invocation_id = invocation_id
        self.state = state

def run_test():
    print("Initializing dynamic logging callback test...\n")
    
    # 1. Create a mock context representing an active agent turn
    mock_context = MockCallbackContext(
        agent_name="ingestion_agent",
        invocation_id="inv-12345-abcde",
        state={"file_name": "tax_return_2025.pdf", "status": "pending"}
    )
    
    # 2. Trigger 'before_agent_callback'
    print("--- Triggering before_agent_callback ---")
    before_agent_callback(mock_context)
    
    # Simulate some agent reasoning/tool execution time
    time.sleep(1.5)
    
    # 3. Trigger 'after_agent_callback'
    print("\n--- Triggering after_agent_callback ---")
    after_agent_callback(mock_context)

if __name__ == "__main__":
    run_test()