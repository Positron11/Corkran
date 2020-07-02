from django.urls import path
from . import views 

urlpatterns = [
    path('mailbox/', views.Mailbox.as_view(), name='mailbox'),
    path('mailbox/<int:pk>/delete/', views.DeleteMail.as_view(), name='delete-mail'),
]