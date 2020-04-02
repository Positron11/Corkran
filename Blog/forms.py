from .models import Comment
from django import forms


# comment creation
class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["content"]