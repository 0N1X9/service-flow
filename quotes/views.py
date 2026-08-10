from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ai.services import generate_quote

from services.models import ServiceRequest

from .models import Quote

from .forms import QuoteForm

from payments.services import can_generate_quote


@login_required
def quote_generate(request, service_id):
    service = get_object_or_404(
        ServiceRequest,
        pk=service_id,
        client__business=request.user.businessprofile,
    )

    if not can_generate_quote(request.user):
        messages.error(
            request,
            (
                "You have reached your monthly AI quote limit. "
                "Upgrade to Premium for unlimited quotes."
            )
        )
        return redirect("payments:upgrade")

    try:
        generation_result = generate_quote(service)

    except Exception:
        messages.error(
            request,
            "The AI quote service is temporarily unavailable. "
            "Please try again later.",
        )
        return redirect("services:list")

    quote_text = generation_result.content

    quote, created = Quote.objects.update_or_create(
        service_request=service,
        defaults={
            "content": quote_text,
            "provider": generation_result.provider,
            "price": service.estimated_price,
            "is_outdated": False,
        },
    )
    # Update the service status to "QUOTED" and save it
    service.status = "QUOTED"
    service.save(update_fields=["status"])

    messages.success(
        request,
        "Quote generated successfully.",
    )

    return redirect(
        "quotes:detail",
        pk=quote.pk,
    )


@login_required
def quote_detail(request, pk):
    quote = get_object_or_404(
        Quote,
        pk=pk,
        service_request__client__business=request.user.businessprofile,
    )

    if request.method == "POST":
        form = QuoteForm(request.POST, instance=quote)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Quote updated successfully.",
            )

            return redirect(
                "quotes:detail",
                pk=quote.pk,
            )

    else:
        form = QuoteForm(instance=quote)

    quote_outdated = quote.is_outdated

    edit_mode = request.GET.get("edit") == "1"

    return render(
        request,
        "quotes/quote_detail.html",
        {
            "quote": quote,
            "form": form,
            "edit_mode": edit_mode,
            "quote_outdated": quote_outdated,
        },
    )


@login_required
def quote_list(request):
    quotes = (
        Quote.objects.filter(
            service_request__client__business=request.user.businessprofile
        )
        .select_related(
            "service_request",
            "service_request__client",
        )
        .order_by("-updated_at")
    )

    return render(
        request,
        "quotes/quote_list.html",
        {
            "quotes": quotes,
        },
    )
