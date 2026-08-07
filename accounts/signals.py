from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import BusinessProfile
from payments.models import Subscription


@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    if created:
        BusinessProfile.objects.create(
            user=instance,
            business_name=f"{instance.username}'s Business",
        )

        Subscription.objects.create(
            user=instance,
        )
