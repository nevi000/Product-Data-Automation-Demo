from app.services.llm.base import EnrichmentResult, LLMProvider
from app.services.llm.mock_provider import MockLLMProvider

__all__ = ["EnrichmentResult", "LLMProvider", "MockLLMProvider", "get_provider"]

_PROVIDERS = {"mock": MockLLMProvider}


def get_provider(name: str = "mock") -> LLMProvider:
    """Return an LLM provider by name.

    Only the deterministic ``mock`` provider ships in this repo so the demo runs
    with no API keys. A real provider (Anthropic / Google / OpenAI) is a drop-in:
    implement `LLMProvider` and register it here.
    """
    try:
        return _PROVIDERS[name]()
    except KeyError:
        raise ValueError(f"unknown LLM provider: {name!r}") from None
