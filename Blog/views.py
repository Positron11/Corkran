from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Article, Announcement, Comment
from next_prev import next_in_order, prev_in_order
from .forms import CommentForm, FeatureArticleForm
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
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

	# latest article as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)                    
		context["featured_article"] = Article.objects.filter(featured=True).first()
		return context


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
	ordering = ['-date']
	context_object_name = "announcements"


# article detail
def detail(request, pk, slug):
	article = get_object_or_404(Article, pk=pk)
	feature_form = FeatureArticleForm()
	comment_form = CommentForm()

	# all articles queryset
	articles = Article.objects.order_by('-date')

	# get next article, or loop around
	if next_in_order(article, articles):
		next_article = next_in_order(article, articles)
	else:
		next_article = articles.first()

	# get previous article, or loop around
	if prev_in_order(article, articles):
		previous_article = prev_in_order(article, articles)
	else:
		previous_article = articles.last()


	# current, next, and previous article, and comment form
	context = {"article": article, "next_article": next_article, "previous_article": previous_article, "comment_form": comment_form, "feature_form": feature_form}

	if request.method == 'POST':
		# if submitting a comment
		if any(x in request.POST for x in ["comment", "reply", "edit"]):
			# if editing comment, set instance to specific comment
			if "edit" in request.POST:
				comment = Comment.objects.get(id=request.POST.get('id'))
				comment_form = CommentForm(request.POST, instance=comment)
			else:
				comment_form = CommentForm(request.POST)

			# if the submitted form is valid
			if comment_form.is_valid():
				# set comment author to currently logged in user
				comment_form.instance.author = request.user

				# set comment article to current article on page
				comment_form.instance.article = article

				# try to get parent id
				try:
					parent_id = int(request.POST.get('parent_id'))
				except:
					parent_id = None

				# if got parent id and parent exists, set parent
				if parent_id:
					parent = Comment.objects.get(id=parent_id)
					if parent:
						comment_form.instance.parent = parent

				# save form
				comment_form.save()

				# display success message
				if "edit" in request.POST:
					messages.success(request, "Comment successfully edited.")
				else:
					messages.success(request, "Comment successfully posted.")

				# redirect to current page and scroll to previous position
				return redirect(article.get_absolute_url())
			else:
				# display error message
				if "edit" in request.POST:
					messages.error(request, "Error editing comment.")
				else:
					messages.error(request, "Error posting comment.")
		# if (un)featuring article
		elif "feature" in request.POST:
			feature_form = FeatureArticleForm(request.POST, instance=article)

			if feature_form.is_valid():
				# unfeature all other articles
				Article.objects.update(featured=False)
				feature_form.save()
				if article.featured:
					messages.success(request, f'"{article.title}" featured.')
				else:
					messages.success(request, f'"{article.title}" unfeatured.')
				return redirect('home')

	return render(request, "Blog/article_detail.html", context)


# create article
class CreateArticle(LoginRequiredMixin, CreateView):
	model = Article
	fields = ["thumbnail", "title", "content", "tags", "attribution"]

	# all tags as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)                     
		context["tags"] = Article.tags.most_common()[:100]
		return context

	# set post author to currently logged in user
	def form_valid(self, form):
		form.instance.author = self.request.user
		messages.success(self.request, f'"{capwords(form.instance.title)}" published.')
		return super().form_valid(form)

	
# edit article
class EditArticle(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Article
	fields = ["thumbnail", "title", "content", "tags", "attribution"]
	template_name_suffix = "_form"

	# all tags as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)                     
		context["tags"] = Article.tags.most_common()[:100]
		return context

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
		return self.request.user == self.get_object().author or self.request.user == self.get_object().article.author