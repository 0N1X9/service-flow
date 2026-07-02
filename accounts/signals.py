from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import BusinessProfile


@receiver(post_save, sender=User)
def create_business_profile(sender, instance, created, **kwargs):
    if created:
        BusinessProfile.objects.create(
            user=instance,
            business_name=f"{instance.username}'s Business",
        )
