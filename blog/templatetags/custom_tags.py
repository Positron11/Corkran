from blog.models import Announcement
from django import template

register = template.Library()


@register.simple_tag
def announcement():
    return Announcement.objects.last().content


