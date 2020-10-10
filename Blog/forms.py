from .models import Article, Comment, Announcement
from django import forms


# new announcement
class AnnouncementForm(forms.ModelForm):

	class Meta:
		model = Announcement
		fields = ["content"]


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
