from django.db import models
from django.contrib.auth.models import User


class Subscription(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True
    )

    plan = models.CharField(
        max_length=50,
        default="free"
    )

    is_active = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    expiration_date = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username
