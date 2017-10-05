import dashboard.views as views

from django.core.urlresolvers import reverse
from django import template
from django.utils.html import mark_safe
from main.models import *
from tasks.models import Solution

import re

register = template.Library()

@register.inclusion_tag('templatetags/dashmenu.html')
def dash_menu(selected, user):
    '''
    The input format of item is: [url, name, count]
    '''
    list = [            
            [reverse(views.articles, args=('articles', 0)), 'Articles',
             Article.objects.filter(author=user, is_published=True).count()], 
            [reverse(views.articles, args=('drafts', 0,)), 'Drafts',
             Article.objects.filter(author=user, is_published=False).count()],
            [reverse(views.my_comments), 'My comments',
             Comment.objects.filter(author=user).count()],
            [reverse(views.comments_to_me), 'Comments to me',
             Comment.objects.filter(article__author=user).exclude(author=user).count()],
            [reverse(views.my_solutions), 'My solutions',
             Solution.objects.filter(author=user).count()],
            [reverse(views.favorites, args=('favorites', 0,)), 'Favorites',
             Favorite.objects.filter(owner=user).count()],
            [reverse(views.private_settings, args=('edit',)), 'Settings',
             ''],
        ]
    return {'dash_menu' : list, 'selected' : selected}


@register.filter
def is_in_favorites(article, user):
    return True if Favorite.objects.filter(article=article, owner=user) else False

@register.filter
def today(value):
    import datetime
    return datetime.date.today()

@register.filter
def replacepre(value):
    return value.replace('pre', 'code')

@register.filter
def highlight(text, query):
    if "\"" in query:
        words = [query.replace("\"", "")]
    else:
        words = query.split()
    for word in words:
        pattern = re.compile(word, re.IGNORECASE)
        entries = re.split(pattern, text)
        items = [m.group(0) for m in re.finditer(pattern, text)]
        new_text = "".join(["".join([entry, "<span class='highlight'>", items[i], "</span>"]) if i<len(items) else entry for i, entry in enumerate(entries)])
        text = new_text
    return mark_safe(new_text)

@register.filter
def truncate_with_query(text, query):
    max_chars = 700
    if "\"" in query:
        words = [query.replace("\"", "")]
    else:
        words = query.split()
    if len(text) > max_chars:
        for i in range(max_chars, len(text), max_chars):
            for word in words:
                if word.lower() in text[i:max_chars+i].lower():
                    return "..." + text[i:max_chars+i] + "..."
        return text[0:max_chars] + "..."
    else:
        return text
