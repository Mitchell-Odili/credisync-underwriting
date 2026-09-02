import time
import functools
from google.api_core.exceptions import ResourceExhausted

def handle_rate_limit(func):
    """Decorator that catches 429 ResourceExhausted errors and automatically 
    pauses to respect the Gemini Free Tier 15 RPM rate limit.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except ResourceExhausted as e:
                sleep_time = 35  # Default safe buffer over the 32s requirement
                print(f"\n[Rate Limit Notice] Free tier 15 RPM quota hit. Pausing for {sleep_time}s to let quota reset...")
                time.sleep(sleep_time)
                print("Resuming execution...\n")
            except Exception as e:
                # Catch general exception strings if wrapped differently
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    sleep_time = 35
                    print(f"\n[Rate Limit Notice] Quota limit hit. Pausing for {sleep_time}s...")
                    time.sleep(sleep_time)
                    print("Resuming execution...\n")
                else:
                    raise e
    return wrapper