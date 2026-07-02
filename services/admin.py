from django.contrib import admin

from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "status",
        "estimated_price",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "title",
        "client__name",
    )
