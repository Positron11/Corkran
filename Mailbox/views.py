from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from next_prev import next_in_order, prev_in_order
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.urls import reverse
from .models import Mail

# mailbox
class Mailbox(LoginRequiredMixin, ListView):
	context_object_name = "mailbox"
	template_name = "Mailbox/mailbox.html"

	def get_queryset(self):
		# get queryset
		queryset = Mail.objects.filter(recipient=self.request.user).order_by("-date")

		# get unread mail
		unread = [mail for mail in queryset.filter(read=False)]

		# pass unread messages to context before marking as read
		self.extra_context = dict()
		self.extra_context["unread"] = unread
		self.extra_context["unread_count"] = len(unread)
		self.extra_context["mailbox_count"] = queryset.count()
		
		# mark all unread messages as read when page visited
		queryset.update(read=True)

		return queryset


# delete mail
class DeleteMail(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Mail

	def get_success_url(self):
		mail = Mail.objects.filter(recipient=self.request.user).order_by('-date')
		if len(mail) > 1:
			return reverse('mailbox') + f"#{next_in_order(self.get_object(), mail).id if next_in_order(self.get_object(), mail) else prev_in_order(self.get_object(), mail).id}"
		else:
			return reverse('mailbox')

	# check if currently logged in user is author
	def test_func(self):
		return self.request.user == self.get_object().recipient