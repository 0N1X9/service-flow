import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request):
    return stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[
            {
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }
        ],
        success_url=request.build_absolute_uri(
            reverse("payments:success")
        ),
        cancel_url=request.build_absolute_uri(
            reverse("payments:cancel")
        ),
        metadata={
            "user_id": request.user.id,
        },
    )
