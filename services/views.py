from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clients.models import Client

from .forms import ServiceRequestForm
from .models import ServiceRequest


@login_required
def service_list(request):
    profile = request.user.businessprofile

    services = (
        ServiceRequest.objects.filter(client__business=profile)
        .select_related("client", "quote")
        .order_by("-created_at")
    )

    for service in services:
        service.quote_outdated = (
            hasattr(service, "quote") 
            and service.quote.is_outdated
        )

    return render(
        request,
        "services/service_list.html",
        {
            "services": services,
        },
    )


@login_required
def service_create(request):
    profile = request.user.businessprofile

    if request.method == "POST":
        form = ServiceRequestForm(request.POST)

        # Only allow the user's own clients
        form.fields["client"].queryset = Client.objects.filter(business=profile)

        if form.is_valid():
            form.save()
            messages.success(request, "Job created successfully.",)
            return redirect("services:list")
    else:
        form = ServiceRequestForm()
        form.fields["client"].queryset = Client.objects.filter(business=profile)

    return render(
        request,
        "services/service_form.html",
        {
            "form": form,
            "title": "Create Job",
        },
    )


@login_required
def service_update(request, pk):
    profile = request.user.businessprofile

    service = get_object_or_404(
        ServiceRequest,
        pk=pk,
        client__business=profile,
    )

    if request.method == "POST":
        form = ServiceRequestForm(request.POST, instance=service,)
        form.fields["client"].queryset = Client.objects.filter(business=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.",)
            return redirect("services:list")
    else:
        form = ServiceRequestForm(instance=service)
        form.fields["client"].queryset = Client.objects.filter(business=profile)
    return render(
        request,
        "services/service_form.html",
        {
            "form": form,
            "title": "Edit Job",
        },
    )


@login_required
def service_delete(request, pk):
    profile = request.user.businessprofile

    service = get_object_or_404(
        ServiceRequest,
        pk=pk,
        client__business=profile,
    )

    if request.method == "POST":
        service.delete()
        messages.success(request, "Job deleted successfully.",)
        return redirect("services:list")
    return render(
        request,
        "services/service_confirm_delete.html",
        {
            "service": service,
        },
    )
