from app.services.llm.base import EnrichmentResult, LLMProvider
from app.services.llm.mock_provider import MockLLMProvider

__all__ = ["EnrichmentResult", "LLMProvider", "MockLLMProvider", "get_provider"]

_PROVIDERS = {"mock": MockLLMProvider}

def get_provider(name: str = "mock") -> LLMProvider:
    try:
        return _PROVIDERS[name]()
    except KeyError:
        raise ValueError(f"unknown LLM provider: {name!r}") from None
