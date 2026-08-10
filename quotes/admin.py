from django.contrib import admin

from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "provider",
        "price",
        "created_at",
        "updated_at",
        "is_outdated",
    )

    list_filter = (
        "provider",
        "is_outdated",
    )

    search_fields = (
        "service_request__title",
        "service_request__client__name",
        "content",
    )
