from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Donation

@receiver(post_save, sender=Donation)
@receiver(post_delete, sender=Donation)
def update_campaign_current_money(sender, instance, **kwargs):
    if instance.campaign:
        instance.campaign.update_current_money()
