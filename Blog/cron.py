from django.template.loader import render_to_string
from django_cron import CronJobBase, Schedule
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from django.core.mail import send_mail
from Blog.models import Comment


class NewCommentsEmailNotification(CronJobBase):
	# run daily
	schedule = Schedule(run_at_times=['24:00'])
	code = 'Corkran.new_comments_email_notification'


	# main cronjob
	def do(self):
		# get queryset of day-old comments
		time_threshold = datetime.now() - timedelta(hours=24)
		new_comments = Comment.objects.filter(date__gt=time_threshold)

		# if any new comments
		if (len(new_comments) > 0):
			self.new_comments_on_article(new_comments)
			self.new_replies(new_comments)

	
	# notifications to article authors about new comments
	def new_comments_on_article(self, new_comments):
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
		
		self.send_email(data, "Blog/new_comments_email.html", "Blog/new_comments_email.txt")


	# notifications to comment authors about replies
	def new_replies(self, new_comments):
		# get replies out of new comments
		new_replies = new_comments.filter(parent__in=Comment.objects.all())

		# new empty dataset
		data = dict()

		# create a dictionary entry for each recipient
		for comment in new_replies:
			data[comment.parent.author] = dict()

		# create an empty list for the replies of each parent comment
		for comment in new_replies:
			data[comment.parent.author][comment.parent] = list()

		# place all replies in their appropriate entries
		for comment in new_replies:
			data[comment.parent.author][comment.parent].append(comment)

		self.send_email(data, "Blog/new_replies_email.html", "Blog/new_replies_email.txt")

	
	# email function
	def send_email(self, data, html_template, text_template):
		# standard email values
		from_email = 'Corkran <noreply@corkran.pythonanywhere.com>' 
		subject = 'New comments on your Corkran articles' 
		
		# for each recipient...
		for recipient in data:
			context = {
				"recipient": recipient.username, 
				"data": data[recipient], 
				"protocol": "https", 
				"domain": "corkran.pythonanywhere.com"
			}

			# html message and plaintext fallback
			html_message = render_to_string(html_template, context)
			plain_message = render_to_string(text_template, context)

			# send email
			send_mail(from_email=from_email, recipient_list=[recipient.email], subject=subject, message=plain_message, html_message=html_message)




