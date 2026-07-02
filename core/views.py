from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import BusinessProfileForm
from clients.models import Client
from services.models import ServiceRequest
from quotes.models import Quote


@login_required
def dashboard(request):
    profile = request.user.businessprofile

    context = {
        "profile": profile,
        "client_count": Client.objects.filter(business=profile).count(),
        "service_count": ServiceRequest.objects.filter(
            client__business=profile
        ).count(),
        "quote_count": Quote.objects.filter(
            service_request__client__business=profile
        ).count(),
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
