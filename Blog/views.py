from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Article, Announcement, Comment
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CommentForm
from string import capwords


class ArticleListView(ListView):
	paginate_by = 5
	context_object_name = "articles"

	def get_queryset(self):
		self.extra_context = dict()

		# try to get search query
		search_query = self.request.GET.get("search")

		# if anything actually searched for, not just empty
		if "search" in self.request.GET and search_query:
			# searched
			self.extra_context["searched"] = True

			# convert search query to lowercase
			search_query = search_query.lower()

			# initialize empty querysets
			authors = User.objects.none()
			title_sorted = Article.objects.none()

			# evaluate each word in search query
			for word in search_query.split():
				# get queryset of matching authors
				authors = authors | User.objects.filter(username__icontains=word)

				# construct queryset of articles with matching titles
				title_sorted = title_sorted | Article.objects.filter(title__icontains=word)

			# construct queryset of articles of matching authors
			author_sorted = Article.objects.filter(author__in=authors)

			# construct queryset of articles with matching tags
			tag_sorted = Article.objects.filter(tags__name__in=search_query.split())

			# return combined querysets
			return (tag_sorted | title_sorted | author_sorted).distinct().order_by('-date')
		else:
			# not searched
			self.extra_context["searched"] = False

			# return all articles
			return Article.objects.all().order_by('-date')


# main page
class Home(ArticleListView):
	template_name = "Blog/home.html"


# sort articles by author
class AuthorSortedArticles(ArticleListView):
	template_name = "Blog/author_sorted_articles.html"

	def get_queryset(self):
		queryset = super().get_queryset()

		# get page's author
		author = get_object_or_404(User, username=self.kwargs.get("author"))

		# add author to context
		self.extra_context["author"] = author

		return queryset.filter(author=author)


# sort articles by tag
class TagSortedArticles(ArticleListView):
	template_name = "Blog/tag_sorted_articles.html"

	def get_queryset(self):
		queryset = super().get_queryset()

		# get page's tag
		tag = self.kwargs.get("tag")

		# check if tag exists
		tag_check = get_list_or_404(Article, tags__name__in=[tag])

		# add tag to context
		self.extra_context["tag"] = tag

		return queryset.filter(tags__name__in=[tag])


# about page
def about(request):
	return render(request, "Blog/about.html")


# announcements page
class Announcements(ListView):
	model = Announcement
	sort_by = ["-date"]


# article detail
def detail(request, pk, slug):
	article = get_object_or_404(Article, pk=pk)
	form = CommentForm()

	# single article and comment form
	context = {"article": article, "form": form}

	if request.method == 'POST':
		# if editing comment, set instance to specific comment
		if "edit" in request.POST:
			comment = Comment.objects.get(id=request.POST.get('id'))
			form = CommentForm(request.POST, instance=comment)
		else:
			form = CommentForm(request.POST)

		# if the submitted form is valid
		if form.is_valid():
			# set comment author to currently logged in user
			form.instance.author = request.user

			# set comment article to current article on page
			form.instance.article = article

			# try to get parent id
			try:
				parent_id = int(request.POST.get('parent_id'))
			except:
				parent_id = None

			# if got parent id and parent exists, set parent
			if parent_id:
				parent = Comment.objects.get(id=parent_id)
				if parent:
					form.instance.parent = parent

			# save form
			form.save()

			# display success message
			if "edit" in request.POST:
				messages.success(request, "Comment successfully edited.")
			else:
				messages.success(request, "Comment successfully posted.")

			# redirect to current page and scroll to previous position
			return redirect(article.get_absolute_url() + "#" + request.POST.get('scroll_pos'))
		else:
			# display error message
			if "edit" in request.POST:
				messages.error(request, "Error editing comment.")
			else:
				messages.error(request, "Error posting comment.")

	return render(request, "Blog/article_detail.html", context)


# create article
class CreateArticle(LoginRequiredMixin, CreateView):
	model = Article
	fields = ["title", "content", "tags"]

	# set post author to currently logged in user
	def form_valid(self, form):
		form.instance.author = self.request.user
		messages.success(self.request, f'"{capwords(form.instance.title)}" published.')
		return super().form_valid(form)

	
# edit article
class EditArticle(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Article
	fields = ["title", "content", "tags"]
	template_name_suffix = "_form"

	# show success message
	def form_valid(self, form):
		messages.success(self.request, f'"{capwords(form.instance.title)}" revised.')
		return super().form_valid(form)

	# check if currently logged in user is author
	def test_func(self):
		return self.request.user == self.get_object().author


# delete article
class DeleteArticle(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Article
	success_url = reverse_lazy('home')

	# check if currently logged in user is author
	def test_func(self):
		return self.request.user == self.get_object().author


# delete article
class DeleteComment(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Comment
	
	# return to article page and scroll to comments on delete
	def get_success_url(self):
		return self.get_object().article.get_absolute_url() + "#comments"

	# check if currently logged in user is author
	def test_func(self):
		return self.request.user == self.get_object().author


def handler404(request):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)