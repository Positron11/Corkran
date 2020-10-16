from django.contrib import admin
from .models import Article, Announcement, Comment, Category

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Announcement)