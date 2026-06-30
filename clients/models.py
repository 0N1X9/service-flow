from django.db import models
from core.models import BusinessProfile


class Client(models.Model):

    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="clients"
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    company = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name
