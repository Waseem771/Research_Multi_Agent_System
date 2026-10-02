import os
import litellm
from dotenv import load_dotenv

load_dotenv()

# ── Read Azure API Key ───────────────────────────────────────
# Priority: st.secrets → .env file → empty string
def _get_secret(key: str) -> str:
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, "")

AZURE_ENDPOINT = "https://tariqahmeshaikh07-6260-resource.services.ai.azure.com/openai/v1"

# ── LiteLLM patch ────────────────────────────────────────────
litellm.drop_params = True
_orig = litellm.completion

def _patched(*args, **kwargs):
    for lst in ([kwargs.get('messages', [])] +
                ([args[1]] if len(args) > 1 and isinstance(args[1], list) else [])):
        for msg in lst:
            if isinstance(msg, dict):
                msg.pop('cache_breakpoint', None)
    return _orig(*args, **kwargs)

litellm.completion = _patched


# ── Build LLM using plain API key ────────────────────────────
def _build_llm(model_name: str, max_tokens: int):
    from crewai import LLM
    api_key = _get_secret("AZURE_API_KEY")
    if not api_key:
        raise ValueError(
            "AZURE_API_KEY not found!\n"
            "Add it to .streamlit/secrets.toml:\n"
            '  AZURE_API_KEY = "your-key-here"'
        )
    return LLM(
        model=f"openai/{model_name}",
        base_url=AZURE_ENDPOINT,
        api_key=api_key,
        temperature=0.5,
        max_tokens=max_tokens
    )


# ── Agent model assignments ───────────────────────────────────
def get_fast_llm():
    """gpt-4.1-nano — fastest, Researcher & Lit Reviewer. Max 200 tokens out."""
    return _build_llm("gpt-4.1-nano-2025-04-14", max_tokens=200)

def get_power_llm():
    """gpt-5.2 — most powerful, Analyst & Orchestrator. Max 300 tokens out."""
    return _build_llm("gpt-5.2-2025-12-11", max_tokens=300)

def get_safe_llm():
    """gpt-4.1-mini — balanced, Fact Checker. Max 150 tokens out."""
    return _build_llm("gpt-4.1-mini-2025-04-14", max_tokens=150)
