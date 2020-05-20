from django.urls import path
from . import views 

urlpatterns = [
    # basic views
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('announcements/', views.Announcements.as_view(), name='announcements'),

    # article management views
    path('articles/new/', views.CreateArticle.as_view(), name='create-article'),
    path('articles/<int:pk>/edit/', views.EditArticle.as_view(), name='edit-article'),
    path('articles/<int:pk>/delete/', views.DeleteArticle.as_view(), name='delete-article'),

    # article detail view
    path('articles/<int:pk>/<str:slug>/', views.detail, name='article-detail'),

    # comment deletion view
    path('comments/<int:pk>/delete/', views.DeleteComment.as_view(), name='delete-comment'),
    
    # sorted article views
	path('users/<str:author>/', views.AuthorSortedArticles.as_view(), name='author-sorted-articles'),
    path('tags/<str:tag>/', views.TagSortedArticles.as_view(), name='tag-sorted-articles'),
]
