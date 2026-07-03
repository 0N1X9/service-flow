from django.db import models
from clients.models import Client


class ServiceRequest(models.Model):

    STATUS_CHOICES = [
        ("NEW", "New"),
        ("QUOTED", "Quoted"),
        ("SCHEDULED", "Scheduled"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="services"
    )

    title = models.CharField(max_length=150)

    description = models.TextField()

    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="NEW"
    )

    estimated_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
