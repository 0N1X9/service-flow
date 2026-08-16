from datetime import date

from quotes.models import Quote

from .models import Subscription

FREE_MONTHLY_QUOTE_LIMIT = 3


def is_premium(user):
    """
    Returns True if the user has an active Premium subscription.
    """
    if user is None or getattr(user, "is_anonymous", False):
        return False

    user_id = getattr(user, "pk", None)
    if user_id is None:
        return False

    return Subscription.objects.filter(
        user_id=user_id,
        plan="premium",
        is_active=True,
    ).exists()


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
