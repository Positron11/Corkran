from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView, CommentDeleteView, TagPostListView
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name="blog-home"),
    path('user/<str:username>/', UserPostListView.as_view(), name="user-posts"),
    path('post/tag:<str:tag>/', TagPostListView.as_view(), name="tag-posts"),
    path('post/<int:pk>/<str:slug>/', PostDetailView.as_view(), name="post-detail"),
    path('post/new', PostCreateView.as_view(), name="post-create"),
    path('post/<int:pk>/update', PostUpdateView.as_view(), name="post-update"),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name="post-delete"),
    path('delete-comment/<int:pk>', CommentDeleteView.as_view(), name="comment-delete"),
    path('about/', views.about, name="blog-about"),
]

