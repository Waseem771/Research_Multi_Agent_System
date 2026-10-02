import os
import litellm
from dotenv import load_dotenv

# Load .env file automatically so GROQ_API_KEY is always available
load_dotenv()

# Tell LiteLLM to drop any unsupported parameters
litellm.drop_params = True

# --- PATCH FOR GROQ cache_breakpoint BUG ---
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

def _build_llm(model_name: str, max_tokens: int = 1024):
    """Internal helper — builds a CrewAI LLM object for the given Groq model."""
    from crewai import LLM
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    return LLM(
        model=f"groq/{model_name}",
        api_key=groq_api_key,
        temperature=0.7,
        max_tokens=max_tokens
    )

# ---------------------------------------------------------------
# THREE MODELS — each assigned by task weight
# ---------------------------------------------------------------

def get_fast_llm():
    """
    openai/gpt-oss-20b  ->  Lightweight & fast (TESTED: PASS).
    Best for: Researcher & Literature Reviewer
    """
    return _build_llm("openai/gpt-oss-20b", max_tokens=800)

def get_power_llm():
    """
    openai/gpt-oss-120b  ->  Most powerful reasoning model (TESTED: PASS).
    Best for: Analyst & Orchestrator
    """
    return _build_llm("openai/gpt-oss-120b", max_tokens=1024)

def get_safe_llm():
    """
    openai/gpt-oss-safeguard-20b  ->  Safety-tuned model (TESTED: PASS).
    Best for: Fact Checker
    """
    return _build_llm("openai/gpt-oss-safeguard-20b", max_tokens=600)
