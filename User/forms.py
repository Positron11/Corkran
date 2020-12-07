from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from .models import Profile
from django import forms


# user registration form
class UserRegistrationForm(UserCreationForm):
	email = forms.EmailField()
	first_name = forms.CharField()
	last_name = forms.CharField()

	class Meta:
		model = User
		fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

	# remove all helptext from form
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for fieldname in self.fields:
			self.fields[fieldname].help_text = None


# user update form
class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()
	first_name = forms.CharField()
	last_name = forms.CharField()

	class Meta:
		model = User
		fields = ["username", "first_name", "last_name", "email"]

	# remove all helptext from form
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for fieldname in self.fields:
			self.fields[fieldname].help_text = None


# profile update form
class ProfileUpdateForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = ["bio"]


# profile update form
class ToggleEmailNotificationForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = ["email_notifications"]

	# submit form on change 
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["email_notifications"].widget.attrs["onChange"] = "this.form.submit()"


# password update form
class PasswordForm(PasswordChangeForm):

	# remove all helptext from form and disable autofocus
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for fieldname in self.fields:
			self.fields[fieldname].help_text = None
			self.fields[fieldname].widget.attrs.pop("autofocus", None)
			self.fields[fieldname].widget.attrs["autocomplete"] = "new-password"


# delete user form
class UserDeleteForm(forms.Form):
	delete_articles = forms.BooleanField(required=False)
	delete_comments = forms.BooleanField(required=False)
	confirm_password = forms.CharField(widget=forms.PasswordInput())

	# get request user
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)

	# confirm password before deleting
	def clean(self):
		cleaned_data = super().clean()
		confirm_password = cleaned_data.get('confirm_password')
		if not check_password(confirm_password, self.user.password):
			self.add_error('confirm_password', 'Incorrect password entered. Something subconsious, perhaps?')
		 