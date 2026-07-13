from payments.models import Subscription


def subscription_context(request):
    """
    Makes the current user's subscription available
    to every template.
    """

    if not request.user.is_authenticated:
        return {
            "subscription": None,
        }

    subscription = Subscription.objects.filter(
        user=request.user
    ).first()

    return {
        "subscription": subscription,
    }
