from .base import AIProvider


class OpenRouterProvider(AIProvider):
    """OpenRouter implementation of the AI quote provider."""

    def generate_quote(self, service_request):
        raise NotImplementedError(
            "OpenRouter provider has not been configured yet."
        )
