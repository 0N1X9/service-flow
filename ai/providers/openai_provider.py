import os

from openai import OpenAI

from .base import AIProvider
from ..prompts import SYSTEM_PROMPT


class OpenAIProvider(AIProvider):
    """OpenAI implementation of the AI quote provider."""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_quote(self, service_request):
        prompt = f"""
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
            model=os.getenv("OPENAI_MODEL"),
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )

        return response.output_text
