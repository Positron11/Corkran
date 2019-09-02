from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    content = RichTextUploadingField(external_plugin_resources=[(
                                        "youtube",
                                        "/static/blog/vendor/ckeditor/youtube/youtube/",
                                        "plugin.js",
                                    )])
    date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = TaggableManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk, "slug": self.slug})


class Comment(models.Model):
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class Announcement(models.Model):
    content = models.TextField()

    def __str__(self):
        return self.content
