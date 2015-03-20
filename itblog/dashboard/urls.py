from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url=reverse_lazy('dash', kwargs={'page_type' : 'articles',
                                                                     'subject_id' : 0}))),
    url(r'^(?P<page_type>articles|drafts)/(?P<subject_id>\d+)$', 'dashboard.views.articles', name='dash'),
    url(r'^mycomments$', 'dashboard.views.my_comments', name='dashmycomments'),
    url(r'^commentstome$', 'dashboard.views.comments_to_me', name='dashcommentstome'),
    url(r'^mysolutions$', 'dashboard.views.my_solutions', name='dashmysolutions'),
    url(r'^(?P<page_type>favorites)/(?P<subject_id>\d+)$', 'dashboard.views.favorites', name='dash'),
    url(r'^settings/(?P<type>edit|saved)$', 'dashboard.views.private_settings', name='privatesettings'),
#     url(r'^settings/changepasswd$', 'django.contrib.auth.views.password_change',
#         {'template_name': 'dashboard/changepasswd.html'}, name='password_change'),
#     url(r'^settings$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    )