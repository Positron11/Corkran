from django.db import models
from datetime import datetime
from django.contrib import messages
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from polymorphic.models import PolymorphicModel
from Blog.models import Comment, Article, Announcement


# base mail model
class Mail(PolymorphicModel):
	recipient = models.ForeignKey(User, related_name="mail", on_delete=models.CASCADE)
	date = models.DateTimeField(default=datetime.now, blank=True)
	email_reminder = models.BooleanField(default=False)
	heading = models.CharField(max_length=100)
	read = models.BooleanField(default=False)

	# show self as heading when queried
	def __str__(self):
		return self.heading

	# get all children
	def get_children(self):
		rel_objs = self._meta.related_objects
		return [getattr(self, x.get_accessor_name()) for x in rel_objs if x.model != type(self)]


# new article mail
class NewAnnouncementMail(Mail):
	announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)


# new article mail
class NewArticleMail(Mail):
	article = models.ForeignKey(Article, on_delete=models.CASCADE)


# new comment mail
class NewCommentMail(Mail):
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


# announcement creation receiver
@receiver(post_save, sender=Announcement)
def new_anouncement_notification(sender, instance, created, **kwargs):
	# if new announcement
	if created:
		# send message to all users
		for user in User.objects.all():
				message_to_all = NewAnnouncementMail(recipient=user, heading=f"New Announcement.", announcement=instance)
				message_to_all.save()


# article creation receiver
@receiver(post_save, sender=Article)
def new_article_notification(sender, instance, created, **kwargs):
	# if new article
	if created:
		# send message to all subscribed users
		for profile in instance.author.subscribed.all():
				message_to_subscribed = NewArticleMail(recipient=profile.user, heading=f"New Article by {instance.author.username}.", article=instance)
				message_to_subscribed.save()


# comment creation receiver
@receiver(post_save, sender=Comment)
def new_comment_notification(sender, instance, created, **kwargs):
	# if new comment
	if created:
		# if the comment is a reply
		if instance.parent:
			if instance.author != instance.parent.author:
				message_to_comment_author = NewCommentMail(recipient=instance.parent.author, heading="New Reply to Your Comment.", article=instance.article, comment=instance)
				message_to_comment_author.save()
			
		# send message to author of article if comment is not by same author
		elif instance.author != instance.article.author:
			message_to_article_author = NewCommentMail(recipient=instance.article.author, heading="New Comment on Your Article.", article=instance.article, comment=instance)
			message_to_article_author.save()
