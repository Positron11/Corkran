from django.contrib import admin
from .models import Article, Announcement, Comment

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Announcement)