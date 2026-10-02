import os
import litellm
from dotenv import load_dotenv

load_dotenv()

# ── Read secrets from Streamlit secrets.toml ────────────────
# Streamlit automatically loads .streamlit/secrets.toml
# Access via: st.secrets["KEY_NAME"]
# We also fall back to environment variables if running outside Streamlit

def _get_secret(key: str, fallback: str = "") -> str:
    """Read from st.secrets first, then os.environ, then fallback."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, fallback))
    except Exception:
        return os.getenv(key, fallback)


# ── Azure config ─────────────────────────────────────────────
AZURE_ENDPOINT      = _get_secret("AZURE_ENDPOINT",
    "https://tariqahmeshaikh07-6260-resource.services.ai.azure.com/openai/v1")
AZURE_CLIENT_ID     = _get_secret("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = _get_secret("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID     = _get_secret("AZURE_TENANT_ID")
AZURE_API_KEY       = _get_secret("AZURE_API_KEY")


# ── Choose authentication method ────────────────────────────
def _get_azure_token() -> str:
    """
    Returns a bearer token for Azure OpenAI.
    Uses ClientSecretCredential if env vars are set (Streamlit Cloud),
    otherwise falls back to DefaultAzureCredential (local az login).
    """
    if AZURE_CLIENT_ID and AZURE_CLIENT_SECRET and AZURE_TENANT_ID:
        # ✅ Streamlit Cloud / CI — uses secrets.toml credentials
        from azure.identity import ClientSecretCredential, get_bearer_token_provider
        credential = ClientSecretCredential(
            tenant_id=AZURE_TENANT_ID,
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET
        )
        provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
        return provider()
    elif AZURE_API_KEY:
        # ✅ Simple API key fallback
        return AZURE_API_KEY
    else:
        # ✅ Local dev — uses  az login
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        credential = DefaultAzureCredential()
        provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")
        return provider()


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


# ── Build LLM ────────────────────────────────────────────────
def _build_llm(model_name: str, max_tokens: int):
    from crewai import LLM
    return LLM(
        model=f"openai/{model_name}",
        base_url=AZURE_ENDPOINT,
        api_key=_get_azure_token(),
        temperature=0.5,
        max_tokens=max_tokens
    )


# ── Agent model assignments (total budget ~4,500 tokens/run) ─
# Agent          Model                    max_tokens  Est. total
# Researcher     gpt-4.1-nano-2025-04-14  200         ~500
# Lit Reviewer   gpt-4.1-nano-2025-04-14  200         ~500
# Analyst        gpt-5.2-2025-12-11       300         ~1000
# Fact Checker   gpt-4.1-mini-2025-04-14  150         ~1050
# Orchestrator   gpt-5.2-2025-12-11       300         ~1500
# ─────────────────────────────────────────────────────────────
# TOTAL ESTIMATE: ~4,550 tokens  ✅ well under 10,000

def get_fast_llm():
    """gpt-4.1-nano — fastest, for Researcher & Lit Reviewer."""
    return _build_llm("gpt-4.1-nano-2025-04-14", max_tokens=200)

def get_power_llm():
    """gpt-5.2 — most powerful, for Analyst & Orchestrator."""
    return _build_llm("gpt-5.2-2025-12-11", max_tokens=300)

def get_safe_llm():
    """gpt-4.1-mini — balanced, for Fact Checker."""
    return _build_llm("gpt-4.1-mini-2025-04-14", max_tokens=150)
