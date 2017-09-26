from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

import dashboard.views


urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('dash', kwargs={'page_type' : 'articles',
                                                                     'subject_id' : 0}))),
    url(r'^(?P<page_type>articles|drafts)/(?P<subject_id>\d+)$', dashboard.views.articles, name='dash'),
    url(r'^mycomments$', dashboard.views.my_comments, name='dashmycomments'),
    url(r'^commentstome$', dashboard.views.comments_to_me, name='dashcommentstome'),
    url(r'^mysolutions$', dashboard.views.my_solutions, name='dashmysolutions'),
    url(r'^(?P<page_type>favorites)/(?P<subject_id>\d+)$', dashboard.views.favorites, name='dash'),
    url(r'^settings/(?P<type>edit|saved)$', dashboard.views.private_settings, name='privatesettings'),
]