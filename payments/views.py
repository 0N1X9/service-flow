import json
import logging

import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Subscription

logger = logging.getLogger(__name__)

from .stripe_service import (
    create_checkout_session,
    create_customer_portal_session,
)

from .services import (
    FREE_MONTHLY_QUOTE_LIMIT,
    monthly_quote_count,
    is_premium,
)


@login_required
def upgrade(request):
    return render(
        request,
        "payments/upgrade.html",
        {
            "used_quotes": monthly_quote_count(request.user),
            "limit": FREE_MONTHLY_QUOTE_LIMIT,
            "is_premium": is_premium(request.user),
        },
    )


@login_required
def checkout(request):
    session = create_checkout_session(request)
    return redirect(session.url)


@login_required
def customer_portal(request):
    subscription = request.user.subscription

    if not subscription.stripe_customer_id:
        messages.error(
            request,
            (
                "We couldn't open your billing portal. "
                "Please contact support if this problem persists."
            ),
        )
        return redirect("payments:upgrade")

    portal = create_customer_portal_session(request)
    return redirect(portal.url)


@login_required
def success(request):
    return render(request, "payments/success.html")


@login_required
def cancel(request):
    return render(request, "payments/cancel.html")


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError, stripe.error.StripeError, TypeError) as exc:
        logger.exception("Stripe webhook verification failed")
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        customer_id = session.get("customer")
        metadata = session.get("metadata") or {}
        user_id = metadata.get("user_id")

        if not user_id:
            logger.error(
                "Stripe webhook missing user_id metadata: %s",
                json.dumps(session, default=str),
            )
            return HttpResponse(status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error("Stripe webhook user not found: %s", user_id)
            return HttpResponse(status=400)

        subscription, _ = Subscription.objects.get_or_create(user=user)

        if customer_id:
            subscription.stripe_customer_id = customer_id
        subscription.plan = "premium"
        subscription.is_active = True
        subscription.save()

    return HttpResponse(status=200)
