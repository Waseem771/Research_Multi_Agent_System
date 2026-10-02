import os
import litellm

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
    llama-3.1-8b-instant  →  Lightweight & fast (real Groq model).
    Best for: Researcher & Literature Reviewer
    (quick tool-call tasks that don't need deep reasoning)
    """
    return _build_llm("llama-3.1-8b-instant", max_tokens=800)

def get_power_llm():
    """
    llama-3.3-70b-versatile  →  Most powerful reasoning model (real Groq model).
    Best for: Analyst & Orchestrator
    (heavy synthesis / writing tasks)
    """
    return _build_llm("llama-3.3-70b-versatile", max_tokens=1024)

def get_safe_llm():
    """
    llama-3.3-70b-versatile  →  Used for fact-checking (real Groq model).
    Best for: Fact Checker
    Note: llama-guard-3-8b is a classification model only; using versatile instead
    for free-text fact-check output.
    """
    return _build_llm("llama-3.3-70b-versatile", max_tokens=600)
