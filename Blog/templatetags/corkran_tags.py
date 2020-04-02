from next_prev import next_in_order, prev_in_order
from Blog.models import Article, Announcement
from django import template


register = template.Library()


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


@register.simple_tag
def next_article_link(current):
	article = next_in_order(current, Article.objects.order_by('pk'))
	if article:
		return article.get_absolute_url()
	else:
		# loop around
		return Article.objects.order_by('pk').first().get_absolute_url()


@register.simple_tag
def previous_article_link(current):
	article = prev_in_order(current, Article.objects.order_by('pk'))
	if article:
		return article.get_absolute_url()
	else:
		# loop around
		return Article.objects.order_by('pk').last().get_absolute_url()


@register.simple_tag
def next_article_title(current):
	article = next_in_order(current, Article.objects.order_by('pk'))
	if article:
		return article.title
	else:
		# loop around
		return Article.objects.order_by('pk').first().title


@register.simple_tag
def previous_article_title(current):
	article = prev_in_order(current, Article.objects.order_by('pk'))
	if article:
		return article.title
	else:
		# loop around
		return Article.objects.order_by('pk').last().title


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