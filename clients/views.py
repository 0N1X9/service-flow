from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import BusinessProfile

from .forms import ClientForm
from .models import Client


@login_required
def client_list(request):
    profile = request.user.businessprofile

    clients = Client.objects.filter(business=profile).order_by("name")

    return render(
        request,
        "clients/client_list.html",
        {
            "clients": clients,
        },
    )


@login_required
def client_create(request):
    profile = request.user.businessprofile

    if request.method == "POST":
        form = ClientForm(request.POST)

        if form.is_valid():
            client = form.save(commit=False)
            client.business = profile
            client.save()

            messages.success(
                request,
                "Client created successfully.",
            )

            return redirect("clients:list")

    else:
        form = ClientForm()

    return render(
        request,
        "clients/client_form.html",
        {
            "form": form,
            "title": "Add Client",
        },
    )


@login_required
def client_update(request, pk):
    profile = request.user.businessprofile

    client = get_object_or_404(
        Client,
        pk=pk,
        business=profile,
    )

    if request.method == "POST":
        form = ClientForm(
            request.POST,
            instance=client,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Client updated successfully.",
            )

            return redirect("clients:list")

    else:
        form = ClientForm(instance=client)

    return render(
        request,
        "clients/client_form.html",
        {
            "form": form,
            "title": "Edit Client",
        },
    )


@login_required
def client_delete(request, pk):
    profile = request.user.businessprofile

    client = get_object_or_404(
        Client,
        pk=pk,
        business=profile,
    )

    if request.method == "POST":
        client.delete()

        messages.success(
            request,
            "Client deleted successfully.",
        )

        return redirect("clients:list")

    return render(
        request,
        "clients/client_confirm_delete.html",
        {
            "client": client,
        },
    )
