from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from clients.models import Client
from payments.models import Subscription
from quotes.models import Quote
from services.models import ServiceRequest

from .forms import BusinessProfileForm


@login_required
def dashboard(request):
    profile = request.user.businessprofile

    subscription = Subscription.objects.filter(
        user=request.user
    ).first()

    client_count = Client.objects.filter(
        business=profile
    ).count()

    service_count = ServiceRequest.objects.filter(
        client__business=profile
    ).count()

    quote_count = Quote.objects.filter(
        service_request__client__business=profile
    ).count()

    monthly_limit = None if subscription and subscription.is_active else 3

    if monthly_limit:
        usage_percent = min(
            int((quote_count / monthly_limit) * 100),
            100,
        )
    else:
        usage_percent = 100

    recent_jobs = (
        ServiceRequest.objects.filter(
            client__business=profile
        )
        .select_related("client")
        .order_by("-updated_at")[:5]
    )

    context = {
        "profile": profile,
        "subscription": subscription,
        "client_count": client_count,
        "service_count": service_count,
        "quote_count": quote_count,
        "monthly_limit": monthly_limit,
        "usage_percent": usage_percent,
        "recent_jobs": recent_jobs,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )


@login_required
def business_profile(request):
    profile = request.user.businessprofile

    if request.method == "POST":
        form = BusinessProfileForm(
            request.POST,
            instance=profile,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Business profile updated successfully.",
            )

            return redirect("core:business-profile")

    else:
        form = BusinessProfileForm(instance=profile)

    return render(
        request,
        "core/business_profile.html",
        {
            "form": form,
        },
    )