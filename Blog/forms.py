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
