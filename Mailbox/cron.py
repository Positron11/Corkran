from django.template.loader import render_to_string
from django_cron import CronJobBase, Schedule
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Mail


class UnreadMailEmail(CronJobBase):
	# run daily
	schedule = Schedule(run_at_times=['23:00'])
	code = 'Corkran.unread_mail_email'

	# main cronjob
	def do(self):
		# get all users and mail
		users = User.objects.all()
		all_mail = Mail.objects.all()

		# get all users with unread mail
		recipients = [user for user in users if not all([mail.read or mail.email_reminder for mail in user.mail.all()])]

		for recipient in recipients:
			recipient_unread_mail = all_mail.filter(recipient=recipient, read=False, email_reminder=False)

			# standard email values
			from_email = 'Corkran <noreply@corkran.pythonanywhere.com>' 
			subject = "You've Got Mail"

			context = {
				"protocol": "https", 
				"recipient": recipient.username, 
				"mailbox": recipient_unread_mail,
				"domain": "corkran.pythonanywhere.com"
			}

			# html message and plaintext fallback
			html_message = render_to_string("Mailbox/unread_mail_email.html", context)
			plain_message = render_to_string("Mailbox/unread_mail_email.txt", context)

			# send email
			send_mail(from_email=from_email, recipient_list=[recipient.email], subject=subject, message=plain_message, html_message=html_message)

			# mark all unread mail as having been reminded by email
			recipient_unread_mail.update(email_reminder=True)
	
		





