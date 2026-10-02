import os
import litellm

# Tell LiteLLM to drop any unsupported parameters
litellm.drop_params = True

# --- PATCH FOR GROQ cache_breakpoint BUG ---
# CrewAI forcefully adds 'cache_breakpoint' to messages, which Groq's API strictly rejects.
# This patch intercepts the messages right before they are sent and deletes the unsupported key.
original_completion = litellm.completion

def patched_completion(*args, **kwargs):
    if 'messages' in kwargs:
        for msg in kwargs['messages']:
            if isinstance(msg, dict) and 'cache_breakpoint' in msg:
                del msg['cache_breakpoint']
    
    if len(args) > 1 and isinstance(args[1], list):
        for msg in args[1]:
            if isinstance(msg, dict) and 'cache_breakpoint' in msg:
                del msg['cache_breakpoint']
                
    return original_completion(*args, **kwargs)

litellm.completion = patched_completion
# -------------------------------------------

def get_llm():
    # In recent versions of CrewAI, passing the litellm string format 
    # is the safest and most compatible way to configure the LLM.
    # CrewAI will automatically use the GROQ_API_KEY from os.environ
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    
    from crewai import LLM
    
    return LLM(
        model="groq/mixtral-8x7b-32768",
        api_key=groq_api_key,
        temperature=0.7
    )
