from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.urls import path
from . import views

urlpatterns = [
	# user account and profile
	path('profile/', views.profile, name='profile'),
	path('account-settings/', views.account_settings, name='settings'),

	# authentication views
	path('register/', views.register, name='registration'),
	path('login/', auth_views.LoginView.as_view(template_name="User/login.html"), name='login'),
	path('logout/', auth_views.LogoutView.as_view(template_name="User/logout.html"), name='logout'),

	# password management views
	path('reset-password/', 
		auth_views.PasswordResetView.as_view(
			template_name="User/password_reset_form.html", 
			email_template_name='User/password_reset_email.txt', 
			html_email_template_name='User/password_reset_email.html', 
			subject_template_name='User/password_reset_subject.txt', 
			success_url=reverse_lazy('password-reset-done')
		), 
		name='password-reset'
	),
	path('reset-password-initiated/', 
		auth_views.PasswordResetDoneView.as_view(template_name="User/password_reset_done.html"), 
		name='password-reset-done'
	),
	path('reset-password-confirm/<uidb64>/<token>/', 
			auth_views.PasswordResetConfirmView.as_view(
			template_name="User/password_reset_confirm.html", 
			success_url=reverse_lazy('password-reset-complete')
		), 
		name='password-reset-confirm'
	),
	path('reset-password-done/', 
		auth_views.PasswordResetCompleteView.as_view(template_name="User/password_reset_complete.html"), 
		name='password-reset-complete'
	),

	# user deletion
	path('on-the-ledge/', views.user_confirm_delete_view, name='confirm-delete-user'),
	path('making-the-leap/', views.user_delete_view, name='delete-user'),
]