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
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    
    from crewai import LLM
    
    # llama-3.3-70b-versatile has a much higher TPM limit on Groq's free tier (6000 TPM per request)
    # and is the most capable open model available on Groq right now.
    # openai/gpt-oss-120b has only 8000 TPM total which is too low for a 5-agent crew.
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=groq_api_key,
        temperature=0.7,
        max_tokens=1024  # Cap each agent reply to 1024 tokens to stay within TPM limits
    )
