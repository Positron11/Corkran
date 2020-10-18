from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from .forms import CommentForm, FeatureArticleForm, AnnouncementForm, ArticleForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Article, Announcement, Comment, Category
from next_prev import next_in_order, prev_in_order
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from string import capwords
import random


class ArticleListView(ListView):
	paginate_by = 5
	context_object_name = "articles"

	def get_base_queryset(self):
		return Article.objects.all() 

	def get_queryset(self):
		self.extra_context = dict()

		# get base queryset
		base_queryset = self.get_base_queryset()

		# try to get search query
		search_query = self.request.GET.get("search")

		# if anything actually searched for, not just empty
		if "search" in self.request.GET and search_query:
			# searched boolean and search query
			self.extra_context["searched"] = True
			self.extra_context["query"] = search_query

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
				title_sorted = title_sorted | base_queryset.filter(title__icontains=word)

			# construct queryset of articles of matching authors
			author_sorted = base_queryset.filter(author__in=authors)

			# construct queryset of articles with matching tags
			tag_sorted = base_queryset.filter(tags__name__in=search_query.split())

			# return combined querysets
			return (tag_sorted | title_sorted | author_sorted).distinct().order_by('-date')
		else:
			# not searched
			self.extra_context["searched"] = False

			# return all articles
			return base_queryset.order_by('-date')

	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs) 

		# get queryset and make sure not empty
		queryset = self.get_queryset() 
		queryset = queryset if len(queryset) else Article.objects.all()

		# get tags in queryset
		matching_tags = [tag for article in queryset for tag in article.tags.all()]

		# popular tag suggestions
		tag_search_suggestions = [[tag.name, reverse_lazy("tag-sorted-articles", args=[tag.name])] for tag in Article.tags.most_common()[:100] if tag in matching_tags]

		# author suggestions
		author_search_suggestions = [[author.username, reverse_lazy("author-sorted-articles", args=[author.username])] for author in User.objects.all()]
		
		# article suggestions
		article_search_suggestions = [[article.title, article.get_absolute_url()] for article in queryset]

		# compile dictionary of suggestions
		search_suggestions = {
			"articles": article_search_suggestions,
			"tags": tag_search_suggestions,
			"authors": author_search_suggestions
		}

		# add context
		context["search_suggestions"] = search_suggestions

		return context
		

# main page
class Home(ArticleListView):
	template_name = "Blog/home.html"

	# featured article as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)                    
		context["featured_article"] = Article.objects.filter(featured=True).first()
		return context


# user library
class Library(LoginRequiredMixin, ArticleListView):
	template_name = "Blog/library.html"

	def get_base_queryset(self):
		return Article.objects.filter(id__in=self.request.user.profile.library.all())

	# article count as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)   

		# get base queryset
		queryset = self.get_base_queryset()

		# get authors in library
		authors = list(set([article.author.username for article in queryset]))
		authors_string = ", ".join(list(authors[:5])[:-1] if len(authors) > 1 else authors)

		# variable suffix
		if len(authors) > 1:
			authors_string += f", {authors[-1]}, and others" if len(authors) > 5 else f", and {authors[-1]}"

		# add context
		context["authors"] = authors_string
		context["article_count"] = Article.objects.filter(id__in=self.request.user.profile.library.all()).count()
		context["latest_five"] = ", ".join([article.title for article in sorted(queryset, key=lambda x: random.random())][:5])

		return context


# sort articles by author
class AuthorSortedArticles(ArticleListView):
	template_name = "Blog/author_sorted_articles.html"

	def get_base_queryset(self):
		# get page's author
		author = get_object_or_404(User, username=self.kwargs.get("author"))

		# return queryset of all articles by author
		return Article.objects.filter(author=author)

	# author and article count as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)   

		# get page's author
		author = get_object_or_404(User, username=self.kwargs.get("author"))

		# add context
		context["author"] = author
		context["article_count"] = Article.objects.filter(author=author).count()

		return context


# sort articles by tag
class TagSortedArticles(ArticleListView):
	template_name = "Blog/tag_sorted_articles.html"

	def get_base_queryset(self):
		# get page's tag
		tag = self.kwargs.get("tag")

		# return queryset of all articles with tag
		return Article.objects.filter(tags__name__in=[tag])

	# tag and article count as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)   

		# get page's tag
		tag = self.kwargs.get("tag")

		# check if tag exists
		tag_check = get_list_or_404(Article, tags__name__in=[tag])

		# get queryset
		queryset = Article.objects.filter(tags__name__in=[tag])
		
		# get authors who have used this tag
		authors = list(set([article.author.username for article in Article.objects.filter(tags__name__in=[tag])]))
		authors_string = ", ".join(list(authors[:5])[:-1] if len(authors) > 1 else authors)

		# variable string
		if len(authors) > 1:
			authors_string += f", {authors[-1]}, and others" if len(authors) > 5 else f", and {authors[-1]}"

		# shuffle queryset
		random.shuffle(list(queryset))

		# add context
		context["tag"] = tag
		context["authors"] = authors_string
		context["author_count"] = len(authors)
		context["article_count"] = queryset.count()
		context["latest_five"] = ", ".join([article.title for article in sorted(queryset, key=lambda x: random.random())][:5])

		return context


# about page
def about(request):
	return render(request, "Blog/about.html")


# privacy policies
def privacy(request):
	return render(request, "Blog/privacy_policy.html")


# disclaimer
def disclaimer(request):
	return render(request, "Blog/disclaimer.html")


# terms and conditions
def terms_conditions(request):
	return render(request, "Blog/terms_and_conditions.html")


# announcements page
def announcements(request):
	# all announcements queryset
	announcements = Announcement.objects.all().order_by("-date")
	
	announcement_form = AnnouncementForm()

	if request.method == 'POST':
		# if creating an announcement
		if "create" in request.POST:
			announcement_form = AnnouncementForm(request.POST)

			# if announcement form is valid
			if announcement_form.is_valid:
				announcement_form.save()

				# display success message
				messages.success(request, "Announcement published.")
			else:
				# display error messsage
				messages.error(request, "Error publishing announcement.")			

	context = {
		"announcements": announcements,
		"announcement_form": announcement_form,
	}

	return render(request, "Blog/announcement_list.html", context)


# delete announcement
class DeleteAnnouncement(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Announcement
	success_url = reverse_lazy('announcements')

	# check if currently logged in user is author
	def test_func(self):
		return self.request.user.is_superuser


# article detail
def detail(request, pk, slug):
	article = get_object_or_404(Article, pk=pk)
	feature_form = FeatureArticleForm(instance=article)
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

	# get random article url
	random_article_url = random.choice(Article.objects.all()).get_absolute_url()

	# check if article is in user's library
	try:
		article_in_library = request.user.profile.library.filter(id=article.id).exists()
	except:
		article_in_library = False

	# check if subscribed to author
	try:
		subscribed = request.user.profile.subscribed.filter(id=article.author.id).exists()
	except:
		subscribed = False

	# get category group and all categories
	if (article.categories.all()):
		all_categories = article.categories.all()
		parent_category = all_categories.first().parent
		sub_categories = [category for category in article.categories.all()]
		categories = {"parent": parent_category, "subcategories": sub_categories}
	else:
		categories = None

	if request.method == 'POST':
		if request.user.is_authenticated:
			# if submitting a comment
			if any(x in request.POST for x in ["comment", "reply", "edit"]):
				# if editing comment, set instance to specific comment
				if "edit" in request.POST:
					comment = Comment.objects.get(id=request.POST.get('id'))
					comment_form = CommentForm(request.POST, instance=comment)
				else:
					comment_form = CommentForm(request.POST)

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
						
				else:
					# display error message
					if "edit" in request.POST:
						messages.error(request, "Error editing comment.")
					else:
						messages.error(request, "Error posting comment.")

				# redirect to current page and scroll to posted comment
				return redirect(article.get_absolute_url() + f"#{comment_form.instance.id}")
						
			# if (un)featuring article
			elif "feature" in request.POST:
				feature_form = FeatureArticleForm(request.POST, instance=article)

				if feature_form.is_valid():
					# unfeature all other articles
					Article.objects.update(featured=False)

					feature_form.save()

					# success message
					featured_state = "featured" if article.featured else "unfeatured"
					messages.success(request, f'"{article.title}" {featured_state}.')

			# if subscribing or unsubscribing from author
			elif "subscribe" in request.POST:
				if request.user != article.author:
					if subscribed:
						request.user.profile.subscribed.remove(article.author)
						messages.success(request, f"Unsubscribed from {article.author.username}. You won't recieve any more mail about {article.author.username}.")
					else:
						request.user.profile.subscribed.add(article.author)
						messages.success(request, f"Subscribed to {article.author.username}. We'll mail you when {article.author.username} writes an article.")
				else:
					messages.error(request, "Subscribing to ourselves, are we? We don't do that here.")
			
			# if adding or removing article from personal library
			elif "library" in request.POST:
				if request.user != article.author:
					if article_in_library:
						request.user.profile.library.remove(article)
						messages.success(request, f'"{article.title}" removed from library.')
					else:
						request.user.profile.library.add(article)
						messages.success(request, f'"{article.title}" saved to library.')
				else:
					messages.error(request, "Quite unnecessary, we assure you. Head over to your profile to see all your articles.")
				
			return redirect(article.get_absolute_url())

		# if not logged in
		else:
			return redirect(f"{reverse_lazy('login')}?next={article.get_absolute_url()}")

	context = {
		"article": article, 
		"subscribed": subscribed,
		"next_article": next_article, 
		"previous_article": previous_article, 
		"article_in_library": article_in_library,
		"random_article_url": random_article_url,
		"categories": categories,
		"similar_articles": article.tags.similar_objects()[:8],
		"comment_form": comment_form, 
		"feature_form": feature_form
	}

	return render(request, "Blog/article_detail.html", context)


# article form
class ArticleFormView(LoginRequiredMixin):
	model = Article
	form_class = ArticleForm

	# function for ordering categories
	def sort_categories(self, category):
		return len(category.name)

	# all tags and categories as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)  
		context["tags"] = Article.tags.most_common()[:100]
		context["categories"] = {group: sorted([category for category in Category.objects.filter(parent=group.id)], key=self.sort_categories) for group in Category.objects.filter(parent__isnull=True)}       
		return context

	# if form invalid
	def form_invalid(self, form):
		# get first field that has an error 
		first = list(form.errors.as_data().keys())[0]
		# get first error message string from field
		message = "".join(form.errors.as_data()[first][0])
		# display error message
		messages.error(self.request, f"{message}")
		return super().form_invalid(form)


# create article
class CreateArticle(ArticleFormView, CreateView):

	# set post author to currently logged in user and show success message
	def form_valid(self, form):
		form.instance.author = self.request.user
		messages.success(self.request, f'"{capwords(form.instance.title)}" published.')
		return super().form_valid(form)

 
# edit article
class EditArticle(ArticleFormView, UserPassesTestMixin, UpdateView):

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
	
	# return to article page and scroll to comments or parent on delete
	def get_success_url(self):
		try:
			anchor = self.get_object().parent.id
		except:
			anchor = "comments"

		return self.get_object().article.get_absolute_url() + "#" + str(anchor)

	# check if currently logged in user is author
	def test_func(self):
		return self.request.user == self.get_object().author or self.request.user == self.get_object().article.author


# list of all categories
def category_list(request):
	# get all main categories
	categories = Category.objects.filter(parent__isnull=True)
	
	# create dictionary of main categories and first eight articles in main category
	articles = {category: set([article for subcategory in Category.objects.filter(parent=category) for article in subcategory.articles.all().order_by("-date")][:8]) for category in categories}
	
	# categories and articles as context
	context = {
		"articles": articles,
	}

	return render(request, "Blog/categories_list.html", context)


# list of category's subcategories
def subcategory_list(request, slug):
	# get subcategories
	main_category = get_object_or_404(Category, slug=slug)
	categories = Category.objects.filter(parent=main_category.id)

	# create dictionary of subcategories and latest eight articles of each
	articles = {category: category.articles.all().order_by("-date")[:8] for category in categories}
	
	# categories and articles as context
	context = {
		"articles": articles,
		"main_category": main_category,
	}

	return render(request, "Blog/subcategories_list.html", context)


# sort articles by category
class CategorySortedArticles(ArticleListView):
	template_name = "Blog/category_sorted_articles.html"

	# category and article count as context
	def get_context_data(self, **kwargs):          
		context = super().get_context_data(**kwargs)   

		# get page's category
		category = get_object_or_404(Category, slug=self.kwargs.get("slug"))

		# add context
		context["category"] = category
		context["article_count"] = self.get_base_queryset().count()

		return context


# sort articles by main category
class MainCategorySortedArticles(CategorySortedArticles, ArticleListView):

	def get_base_queryset(self):
		# get page's category
		category = get_object_or_404(Category, slug=self.kwargs.get("slug"))
		subcategories = Category.objects.filter(parent=category)

		# return queryset of all articles in category
		return Article.objects.filter(categories__in=subcategories).distinct()


# sort articles by subcategory
class SubCategorySortedArticles(CategorySortedArticles, ArticleListView):

	def get_base_queryset(self):
		# get page's category
		category = get_object_or_404(Category, slug=self.kwargs.get("slug"))

		# return queryset of all articles in category
		return category.articles.all()