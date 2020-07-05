from .models import Article, Comment
from django import forms


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
