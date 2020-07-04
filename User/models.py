from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# profile model
class Profile(models.Model):
	bio = models.TextField(max_length=500, default="")
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	subscribed = models.ManyToManyField(User, related_name="subscribed", blank=True, symmetrical=False)

	# show self as owner's username
	def __str__(self):
		return self.user.username


# automatically create profile for user
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
		instance.profile.save()
