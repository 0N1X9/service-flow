from datetime import date
from openai import OpenAI
from django.conf import settings

from .base import AIProvider
from ..prompts import SYSTEM_PROMPT


class OpenRouterProvider(AIProvider):
    """OpenRouter implementation of the AI quote provider."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    def generate_quote(self, service_request):
        prompt = f"""
Date:
{date.today():%d %B %Y}

Client:
{service_request.client.name}

Job Title:
{service_request.title}

Description:
{service_request.description}

Estimated Price:
{service_request.estimated_price}
"""

        response = self.client.responses.create(
            model=settings.OPENROUTER_MODEL,
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )

        return response.output_text
