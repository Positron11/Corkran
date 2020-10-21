from Blog.models import Article, Announcement
from Mailbox.models import Mail
from django import template
import re


register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
	

@register.filter
def to_class_name(value):
    return "_".join(re.findall('[A-Z][^A-Z]*', value.__class__.__name__)).lower()


@register.simple_tag
def mailbox_status(user):
	return "read" if all([mail.read for mail in Mail.objects.filter(recipient=user)]) else "unread"


@register.simple_tag
def unread_mail_count(user):
	return len([mail for mail in Mail.objects.filter(recipient=user) if not mail.read])


@register.simple_tag
def latest_article_title():
	if len(Article.objects.all()):
		return Article.objects.order_by('-date').first().title
	else:
		return "New article? How about no article?"


@register.simple_tag
def latest_article_link():
	if len(Article.objects.all()):
		return Article.objects.order_by('-date').first().get_absolute_url()
	else:
		return ""


@register.simple_tag
def latest_announcement():
	if len(Announcement.objects.all()):
		content = Announcement.objects.order_by('-date').first().content
		return content
	else:
		return "Here's an announcement: \"There's nothing here\"."


@register.filter(is_safe=True)
def cut_page_range(page_range, page):
	if len(page_range) <= 5:
		return page_range
	elif page < 4:
		return page_range[:5]
	elif page > (page_range[-1] - 3):
		return page_range[-5:]
	else:
		return page_range[page - 3:page + 2]


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.inclusion_tag('Blog/article_widget_grid.html')
def article_widget_grid(articles):
	return {"articles": articles}