from datetime import date
from django.conf import settings
from google import genai

from .base import AIProvider
from ..prompts import SYSTEM_PROMPT


class GeminiProvider(AIProvider):
    """Google Gemini implementation of the AI quote provider."""

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def is_available(self):
        return bool(
            settings.GEMINI_API_KEY
            and settings.GEMINI_MODEL
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

        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
            },
        )

        return response.text
