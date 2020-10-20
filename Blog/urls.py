from django.urls import path
from . import views 

urlpatterns = [
    # basic views
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('terms-and-conditions/', views.terms_conditions, name='terms-and-conditions'),
    path('announcements/', views.announcements, name='announcements'),

    # announcement deletion view
    path('announcements/<int:pk>/delete/', views.DeleteAnnouncement.as_view(), name='delete-announcement'),

    # user library
    path('library/', views.Library.as_view(), name='library'),

    # article management views
    path('articles/new/', views.CreateArticle.as_view(), name='create-article'),
    path('articles/<int:pk>/edit/', views.EditArticle.as_view(), name='edit-article'),
    path('articles/<int:pk>/delete/', views.DeleteArticle.as_view(), name='delete-article'),

    # article detail view
    path('articles/<int:pk>/<str:slug>/', views.detail, name='article-detail'),

    # comment deletion view
    path('comments/<int:pk>/delete/', views.DeleteComment.as_view(), name='delete-comment'),
    
    # category views
    path('categories/', views.category_list, name='categories'),
    
    # sorted article views
    path('tags/<str:tag>/', views.TagSortedArticles.as_view(), name='tag-sorted-articles'),
	path('users/<str:author>/', views.AuthorSortedArticles.as_view(), name='author-sorted-articles'),
    path('categories/<str:slug>/', views.CategorySortedArticles.as_view(), name='category-sorted-articles'),
]
