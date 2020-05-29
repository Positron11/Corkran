from django.urls import path
from . import views

urlpatterns = [
    path('', views.lounge_index, name='lounges'),
    path('<str:room_name>/', views.lounge, name='lounge'),
]