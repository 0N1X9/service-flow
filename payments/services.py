from datetime import date

from quotes.models import Quote

FREE_MONTHLY_QUOTE_LIMIT = 3


def is_premium(user):
    """
    Returns True if the user has an active Premium subscription.
    """
    return (
        hasattr(user, "subscription")
        and user.subscription.is_active
        and user.subscription.plan == "premium"
    )


def monthly_quote_count(user):
    """
    Returns the number of quotes generated this month.
    """
    today = date.today()

    return Quote.objects.filter(
        service_request__client__business=user.businessprofile,
        created_at__year=today.year,
        created_at__month=today.month,
    ).count()


def can_generate_quote(user):
    """
    Returns True if the user can generate another AI quote.
    """
    if is_premium(user):
        return True

    return monthly_quote_count(user) < FREE_MONTHLY_QUOTE_LIMIT
