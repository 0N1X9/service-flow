from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ai.services import generate_quote

from services.models import ServiceRequest

from .models import Quote


@login_required
def quote_generate(request, service_id):
    service = get_object_or_404(
        ServiceRequest,
        pk=service_id,
        client__business=request.user.businessprofile,
    )

    quote_text = generate_quote(service)

    quote, created = Quote.objects.update_or_create(
        service_request=service,
        defaults={
            "content": quote_text,
            "price": service.estimated_price,
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

    return render(
        request,
        "quotes/quote_detail.html",
        {
            "quote": quote,
        },
    )
