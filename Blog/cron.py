from django.template.loader import render_to_string
from django_cron import CronJobBase, Schedule
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from django.core.mail import send_mail
from Blog.models import Comment


class NewCommentsEmailNotification(CronJobBase):
	# run daily
	schedule = Schedule(run_every_mins=1440)
	code = 'Corkran.new_comments_email_notification'

	def do(self):
		# get queryset of day-old comments
		time_threshold = datetime.now() - timedelta(hours=24)
		new_comments = Comment.objects.filter(date__gt=time_threshold)

		# if any new comments
		if (len(new_comments) > 0):
			# new empty dataset
			data = dict()

			# create a dictionary of recipients to their articles
			for comment in new_comments:
				data[comment.article.author] = dict()

			# create an empty list for comments for each article
			for comment in new_comments:
				data[comment.article.author][comment.article] = list()

			# add comments into appropriate lists
			for comment in new_comments:
				data[comment.article.author][comment.article].append(comment)

			# standard email values
			from_email = 'Corkran <noreply@corkran.pythonanywhere.com>' 
			subject = 'New comments on your Corkran articles' 
			
			# for each recipient...
			for recipient in data:
				context = {
					"recipient": recipient.username, 
					"articles": data[recipient], 
					"protocol": "https", 
					"domain": "corkran.pythonanywhere.com"
				}

				# html message and plaintext fallback
				html_message = render_to_string('Blog/new_comments_email.html', context)
				plain_message = render_to_string('Blog/new_comments_email.txt', context)

				# send email
				send_mail(from_email=from_email, recipient_list=[recipient.email], subject=subject, message=plain_message, html_message=html_message)






