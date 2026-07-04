from django.contrib import admin

from .models import Quote


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "price",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "service_request__title",
    )
