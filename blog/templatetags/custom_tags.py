from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def post_formatter(text):
    formatters = {"b": ["<span style='font-weight: bold'>", "</span>"],
                  "i": ["<span style='font-style: italic'>", "</span>"],
                  "q": ['<blockquote><em>"', '"</em></blockquote>'],
                  "h": ['<mark>', '</mark>']}
    open_tags = []
    final = str()
    for word in text.split("*"):
        if word in formatters.keys():
            if word not in open_tags:
                final += formatters[word][0]
                open_tags.append(word)
            else:
                final += formatters[word][1]
                open_tags.remove(word)
        else:
            final += f"{word}"
    return mark_safe(final)

