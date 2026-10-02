import os
import litellm
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

load_dotenv()

# ── Azure config ────────────────────────────────────────────
AZURE_ENDPOINT = "https://tariqahmeshaikh07-6260-resource.services.ai.azure.com/openai/v1"

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

# ── Token budget per agent (total target < 10,000 tokens) ──
# Agent         Input est.   Output limit   Total
# Researcher    ~300         200            ~500
# Lit Reviewer  ~300         150            ~450
# Analyst       ~700         250            ~950
# Fact Checker  ~900         150            ~1050
# Orchestrator  ~1200        300            ~1500
# ─────────────────────────────────────────────────────────
# Grand total estimate: ~4,450 tokens  ✅ well under 10,000

litellm.drop_params = True

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


def _build_llm(model_name: str, max_tokens: int):
    """Builds a CrewAI LLM with a hard max_tokens cap."""
    from crewai import LLM
    token = token_provider()
    return LLM(
        model=f"openai/{model_name}",
        base_url=AZURE_ENDPOINT,
        api_key=token,
        temperature=0.5,    # lower = more focused, fewer filler tokens
        max_tokens=max_tokens
    )


# ── Model assignments with strict token caps ────────────────

def get_fast_llm():
    """
    gpt-4.1-nano-2025-04-14 — fastest model.
    max_tokens=200 → Researcher & Lit Reviewer output capped at ~200 tokens each.
    """
    return _build_llm("gpt-4.1-nano-2025-04-14", max_tokens=200)


def get_power_llm():
    """
    gpt-5.2-2025-12-11 — most capable model.
    max_tokens=300 → Analyst & Orchestrator capped at ~300 tokens each.
    """
    return _build_llm("gpt-5.2-2025-12-11", max_tokens=300)


def get_safe_llm():
    """
    gpt-4.1-mini-2025-04-14 — balanced model.
    max_tokens=150 → Fact Checker output capped at ~150 tokens.
    """
    return _build_llm("gpt-4.1-mini-2025-04-14", max_tokens=150)
