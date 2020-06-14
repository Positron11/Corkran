from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, PasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import DeleteView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.dispatch import receiver
from django.shortcuts import render
from django.contrib import messages
from Blog.models import Article
from taggit.models import Tag
from django.db.models import Count

# registration page
def register(request):
	form = UserRegistrationForm()

	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)

		if form.is_valid():
			form.save()
			messages.success(request, "Your account has been created. You can now log in.")
			return redirect('home')

	return render(request, 'User/user_registration.html', {"form": form})


# profile page
@login_required
def profile(request):
	user_form = UserUpdateForm(instance=request.user)
	profile_form = ProfileUpdateForm(instance=request.user.profile)
	password_form = PasswordForm(request.user)
	articles = Article.objects.filter(author=request.user)
	tags = Tag.objects.filter(article__in=[article.id for article in articles]).annotate(c=Count('id')).order_by('-c')

	if request.method == 'POST':
		# if password change request
		if 'change_password' in request.POST:
			password_form = PasswordForm(request.user, request.POST)

			# if form valid
			if password_form.is_valid():
				user = password_form.save()
				update_session_auth_hash(request, user)

				# success message
				messages.success(request, "Password successfully updated.")
			else:
				# get first field that has an error 
				first = list(password_form.errors.as_data().keys())[0]

				# get first error message string from field
				message = "".join(password_form.errors.as_data()[first][0])

				# error message
				messages.error(request, f"{message}")
		else:
			user_form = UserUpdateForm(request.POST, instance=request.user)
			profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

			# if both forms valid
			if user_form.is_valid() and profile_form.is_valid():
				user_form.save()
				profile_form.save()

				# success message
				messages.success(request, "Your details have been updated.")
			else:
				# error message
				messages.error(request, "Error updating profile.")

		# redirect to profile
		return redirect('profile')

	# profile update, user details update, and password update form
	context = {"user_form": user_form, "profile_form": profile_form, "password_form": password_form, "articles": articles, "tags":tags}

	return render(request, 'User/user_profile.html', context)


# delete user
class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = User
	template_name = 'User/user_confirm_delete.html'

	def get_success_url(self):
		messages.success(self.request, "You no longer exist.")
		return reverse_lazy('home')

	# check if current user is the user being deleted
	def test_func(self):
		return self.request.user == self.get_object()


# show message on login
@receiver(user_logged_in)
def on_user_logged_in(sender, request, **kwargs):
    return messages.success(request, f"Welcome, {request.user.username}.")


# show message on logout
@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    return messages.success(request, "Logged out.")