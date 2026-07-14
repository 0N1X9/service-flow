# OpenAI calls
import os

from django.conf import settings
from .mock_generator import generate_mock_quote

from .prompts import SYSTEM_PROMPT
from openai import OpenAI
from openai import OpenAIError

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_quote(service_request):
    """
    Generates a quotation.

    In development, a mock quotation is returned.
    In production, OpenAI will be used.
    """
    if settings.DEBUG:
        return generate_mock_quote(service_request)

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

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL"),
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )

        return response.output_text

    except Exception as e:
        print("OpenAI Error:", e)
        return generate_mock_quote(service_request)
