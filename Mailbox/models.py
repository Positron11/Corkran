from django.db import models
from datetime import datetime
from django.contrib import messages
from django.dispatch import receiver
from Blog.models import Comment, Article
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from model_utils.managers import InheritanceManager


# base mail model
class Mail(models.Model):
	recipient = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateTimeField(default=datetime.now, blank=True)
	heading = models.CharField(max_length=100)
	read = models.BooleanField(default=False)
	objects = InheritanceManager()

	# show self as heading when queried
	def __str__(self):
		return self.heading


# new comment mail
class NewCommentMail(Mail, models.Model):
	mail_type = models.CharField(max_length=100)
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)


# comment creation reciever
@receiver(post_save, sender=Comment)
def notify_reply(sender, instance, created, **kwargs):
	# if new comment
	if created:
		# if the comment is a reply
		if instance.parent:
			if instance.author != instance.parent.author:
				message_to_comment_author = NewCommentMail(mail_type="new_reply_mail", recipient=instance.parent.author, heading="New Reply to Your Comment.", article=instance.article, comment=instance)
				message_to_comment_author.save()
			
		# send message to author of article if comment is not by same author
		elif instance.author != instance.article.author:
			message_to_article_author = NewCommentMail(mail_type="new_comment_mail", recipient=instance.article.author, heading="New Comment on Your Article.", article=instance.article, comment=instance)
			message_to_article_author.save()
