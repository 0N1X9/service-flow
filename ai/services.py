from django.conf import settings

from .providers.gemini import GeminiProvider
from .providers.groq import GroqProvider
from .providers.mock import MockProvider
from .providers.openai_provider import OpenAIProvider
from .providers.openrouter import OpenRouterProvider


PROVIDERS = {
    "gemini": GeminiProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "openai": OpenAIProvider,
    "mock": MockProvider,
}


AUTO_PROVIDER_ORDER = [
    "gemini",
    "groq",
    "openrouter",
    "openai",
    "mock",
]


def get_provider():
    """Return the configured AI provider."""
    provider_name = settings.AI_PROVIDER.lower()

    provider_class = PROVIDERS.get(provider_name)

    if provider_class is None:
        raise ValueError(
            f"Unknown AI provider: {provider_name}"
        )

    return provider_class()


def generate_quote(service_request):
    """Generate a quote using the configured AI provider."""

    if settings.AI_PROVIDER.lower() == "auto":
        return generate_quote_auto(service_request)

    provider = get_provider()

    return provider.generate_quote(service_request)


def generate_quote_auto(service_request):
    """Generate a quote using automatic provider fallback."""

    for provider_name in AUTO_PROVIDER_ORDER:
        provider = PROVIDERS[provider_name]()

        if not provider.is_available():
            continue

        try:
            return provider.generate_quote(service_request)

        except Exception as exc:
            print(
                f"AI provider '{provider_name}' failed: {exc}"
            )
            continue

    raise RuntimeError(
        "All AI quote providers are unavailable."
    )
