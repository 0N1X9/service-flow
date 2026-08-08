from .base import AIProvider


class GroqProvider(AIProvider):
    """Groq implementation of the AI quote provider."""

    def generate_quote(self, service_request):
        raise NotImplementedError(
            "Groq provider has not been configured yet."
        )
