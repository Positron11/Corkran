from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import Mail

# mailbox
class Mailbox(LoginRequiredMixin, ListView):
	context_object_name = "mailbox"
	template_name = "Mailbox/mailbox.html"

	def get_queryset(self):
		# get queryset
		queryset = Mail.objects.filter(recipient=self.request.user).order_by("-date").select_subclasses()

		# pass unread messages to context before marking as read
		self.extra_context = dict()
		self.extra_context["unread"] =  [mail for mail in queryset.filter(read=False)]
		
		# mark all unread messages as read when page visited
		queryset.update(read=True)

		return queryset


# delete mail
class DeleteMail(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Mail
	success_url = reverse_lazy('mailbox')

	# check if currently logged in user is author
	def test_func(self):
		return self.request.user == self.get_object().recipient