from datetime import date


def generate_mock_quote(service_request):
    """
    Generates a realistic quotation for development.
    """

    price = (
        f"£{service_request.estimated_price}"
        if service_request.estimated_price
        else "To be confirmed"
    )

    return f"""
QUOTATION

Date: {date.today():%d %B %Y}

Dear {service_request.client.name},

Thank you for contacting us regarding your request.

Job:
{service_request.title}

Description:
{service_request.description}

Scope of Work

• Supply labour required for the work
• Complete the requested service professionally
• Test completed work before handover
• Leave the work area clean and tidy

Estimated Price:
{price}

This quotation is valid for 30 days.

If you have any questions, please don't hesitate to contact us.

Kind regards,

Service Flow AI
"""
