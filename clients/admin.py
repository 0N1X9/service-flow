from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "business",
        "email",
        "phone",
        "created_at",
    )

    search_fields = (
        "name",
        "company",
        "email",
    )

    list_filter = (
        "business",
    )
