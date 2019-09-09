from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView, AnnouncementListView, CommentDeleteView, TagPostListView
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name="blog-home"),
    path('announcements', AnnouncementListView.as_view(), name="blog-announcements"),
    path('users/<str:username>/', UserPostListView.as_view(), name="user-posts"),
    path('posts/tag:<str:tag>/', TagPostListView.as_view(), name="tag-posts"),
    path('posts/<int:pk>/<str:slug>/', PostDetailView.as_view(), name="post-detail"),
    path('posts/new', PostCreateView.as_view(), name="post-create"),
    path('posts/<int:pk>/update', PostUpdateView.as_view(), name="post-update"),
    path('posts/<int:pk>/delete', PostDeleteView.as_view(), name="post-delete"),
    path('delete-comment/<int:pk>', CommentDeleteView.as_view(), name="comment-delete"),
    path('about/', views.about, name="blog-about"),
]

