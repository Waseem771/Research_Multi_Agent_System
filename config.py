import os
import litellm
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Load .env file automatically
load_dotenv()

# ---------------------------------------------------------------
# AZURE OPENAI CONFIG
# ---------------------------------------------------------------
AZURE_ENDPOINT = "https://tariqahmeshaikh07-6260-resource.services.ai.azure.com/openai/v1"

# Azure token provider (works locally with: az login)
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

# ---------------------------------------------------------------
# AVAILABLE MODELS (all tested ✅)
# ---------------------------------------------------------------
# [1]  gpt-4o-mini-2024-07-18      → Fast & cheap
# [2]  gpt-4o-2024-11-20           → Balanced, strong vision
# [3]  gpt-4.1-2025-04-14          → Advanced reasoning
# [4]  gpt-4.1-mini-2025-04-14     → Fast + smart
# [5]  gpt-4.1-nano-2025-04-14     → Fastest, lightest
# [6]  gpt-5-2025-08-07            → Most powerful GPT-5
# [7]  gpt-5-mini-2025-08-07       → GPT-5 fast version
# [8]  gpt-5-nano-2025-08-07       → GPT-5 ultra-fast
# [9]  gpt-5.1-2025-11-13          → Latest GPT-5.1
# [10] gpt-5.2-2025-12-11          → Cutting-edge GPT-5.2
# ---------------------------------------------------------------

# Tell LiteLLM to drop any unsupported parameters
litellm.drop_params = True

# --- PATCH FOR cache_breakpoint BUG ---
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
# ---------------------------------------


def _build_llm(model_name: str, max_tokens: int = 1024):
    """
    Builds a CrewAI LLM using Azure OpenAI endpoint + Azure token auth.
    Fetches a fresh token each call so it never expires mid-run.
    """
    from crewai import LLM
    token = token_provider()   # fresh Azure bearer token
    return LLM(
        model=f"openai/{model_name}",   # openai/ prefix tells LiteLLM to use OpenAI-compatible API
        base_url=AZURE_ENDPOINT,
        api_key=token,
        temperature=0.7,
        max_tokens=max_tokens
    )


# ---------------------------------------------------------------
# AGENT MODEL ASSIGNMENTS (by task weight)
# ---------------------------------------------------------------

def get_fast_llm():
    """
    gpt-4.1-nano-2025-04-14  →  Fastest & lightest Azure model.
    Best for: Researcher & Literature Reviewer
    (quick web search + summarization tasks)
    """
    return _build_llm("gpt-4.1-nano-2025-04-14", max_tokens=800)


def get_power_llm():
    """
    gpt-5.2-2025-12-11  →  Most powerful & latest Azure model.
    Best for: Analyst & Orchestrator
    (deep reasoning, synthesis, final report writing)
    """
    return _build_llm("gpt-5.2-2025-12-11", max_tokens=1500)


def get_safe_llm():
    """
    gpt-4.1-mini-2025-04-14  →  Smart & balanced Azure model.
    Best for: Fact Checker
    (verification, flagging inaccuracies, critical review)
    """
    return _build_llm("gpt-4.1-mini-2025-04-14", max_tokens=600)
