from .base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini implementation of the AI quote provider."""

    def generate_quote(self, service_request):
        raise NotImplementedError(
            "Gemini provider has not been configured yet."
        )
