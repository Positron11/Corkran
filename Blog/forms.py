from .models import Article, Comment, Announcement, Category
from django import forms


# new announcement
class AnnouncementForm(forms.ModelForm):

	class Meta:
		model = Announcement
		fields = ["content"]


# article form
class ArticleForm(forms.ModelForm):
	category = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=Category.objects.all(), required=False)

	class Meta:
		model = Article
		fields = ["thumbnail", "title", "lede", "content", "tags", "category", "attribution"]

	# set lede textbox height and field placeholders 
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["lede"].widget.attrs["rows"] = "3"
		self.fields["lede"].widget.attrs["placeholder"] = "Short paragraph of introduction, or summary..."
		self.fields["title"].widget.attrs["placeholder"] = "Give it a name..."
		self.fields["content"].widget.attrs["placeholder"] = "Il n'y a pas de hors-texte..."
		self.fields["tags"].widget.attrs["placeholder"] = "Eg. Halfling, Vigeneré..."

	# make category mandatory in form
	def clean(self):
		cleaned_data = super().clean()
		category = cleaned_data.get('category')
		if not category:
			raise forms.ValidationError("You have not selected a category.")


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
