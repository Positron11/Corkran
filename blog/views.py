from .models import Post, Comment, Announcement
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.template.defaultfilters import slugify


class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"
    paginate_by = 5
    is_search = bool

    def get_queryset(self):
        if "search" in self.request.GET:
            search_query = self.request.GET.get('search', "").lower()
            users = User.objects.filter(username__icontains=search_query).all()
            posts = Post.objects.filter(Q(tags__name__in=search_query.split()) | Q(title__icontains=search_query) | Q(author__in=users)).order_by("tags", "title", "author")
            self.extra_context = {'is_search': True}
        else:
            posts = Post.objects.all()
            self.extra_context = {'is_search': False}
        return posts.order_by("-date").distinct()


class UserPostListView(PostListView):
    template_name = "blog/user_posts.html"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return super().get_queryset().filter(author=user)


class TagPostListView(PostListView):
    template_name = "blog/tag_posts.html"

    def get_queryset(self):
        tag = self.kwargs.get("tag")
        return super().get_queryset().filter(tags__name__in=[tag])


class PostView(DetailView):
    model = Post
    pass


class CommentView(CreateView):
    model = Comment
    fields = ["content"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = self.get_object(Post.objects.all())
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'slug': self.get_object(Post.objects.all()).slug,
                                                   'pk': self.get_object(Post.objects.all()).id})
    pass


class PostDetailView(View):
    def get(self, request, *args, **kwargs):
        view = PostView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs) :
        view = CommentView.as_view()
        return view(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "content", "tags"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.slug = slugify(form.instance.title)
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content", "tags"]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.user or self.request.user == comment.post.author:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'slug': self.get_object(Comment.objects.all()).post.slug,
                                                   'pk': self.get_object(Comment.objects.all()).post.id})


class AnnouncementListView(ListView):
    model = Announcement
    template_name = "blog/announcements.html"
    context_object_name = "announcements"
    ordering = ["-date"]
    paginate_by = 10


def about(request):
    return render(request, "blog/about.html")

