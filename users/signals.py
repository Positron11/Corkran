from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Setting


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def create_setting(sender, instance, created, **kwargs):
    if created:
        Setting.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_setting(sender, instance, **kwargs):
    instance.setting.save()



