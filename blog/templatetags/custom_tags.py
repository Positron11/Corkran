from blog.models import Announcement, Post
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django import template

register = template.Library()


@register.simple_tag
def latest_post():
    post = Post.objects.last()
    return mark_safe(f"<a href='{reverse_lazy('post-detail', kwargs={'slug': post.slug, 'pk': post.id})}'>{post.title}</a>",)


@register.simple_tag
def user_latest_post(username):
    post = User.objects.filter(username=username).first().post_set.last()
    return mark_safe(f"<a href='{reverse_lazy('post-detail', kwargs={'slug': post.slug, 'pk': post.id})}'>{post.title}</a>")


@register.simple_tag
def user_post_count(username):
    count = User.objects.filter(username=username).first().post_set.count()
    return count


@register.simple_tag
def tag_post_count(tag):
    count = Post.objects.filter(tags__name__in=[tag]).count()
    return count


@register.simple_tag
def announcement():
    if Announcement.objects.count() != 0:
        return mark_safe(f"{Announcement.objects.last().content} <span class='subheading right'>-{Announcement.objects.last().date.strftime('%B %-d, %Y')}</span>")
    else:
        return "No Announcements"


