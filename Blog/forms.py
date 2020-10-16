from .models import Article, Comment, Announcement, Category
from django import forms


# new announcement
class AnnouncementForm(forms.ModelForm):

	class Meta:
		model = Announcement
		fields = ["content"]


# article form
class ArticleForm(forms.ModelForm):
	categories = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Category.objects.all(), required=False)

	class Meta:
		model = Article
		fields = ["thumbnail", "title", "content", "tags", "categories", "attribution"]

	# restrict categories to one main group
	def clean(self):
		# get article's categories
		categories = self.cleaned_data.get("categories")
		# if subcategories under more than one main category raise error
		if len(set([category.parent for category in categories])) > 1:
			raise forms.ValidationError("You can only choose subcategories under one category.")	
		return self.cleaned_data


# comment creation
class CommentForm(forms.ModelForm):

	class Meta:
		model = Comment
		fields = ["content"]


# feature article
class FeatureArticleForm(forms.ModelForm):

	class Meta:
		model = Article
		fields = ["featured"]

	# submit form on change 
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["featured"].widget.attrs["onChange"] = "this.form.submit()"
