from django.db import models
from services.models import ServiceRequest


class Quote(models.Model):

    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="quote"
    )

    content = models.TextField()

    provider = models.CharField(
        max_length=50,
        default="unknown",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    is_outdated = models.BooleanField(default=False)

    def __str__(self):
        return f"Quote - {self.service_request.title}"
