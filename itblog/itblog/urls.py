from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/articles/blog/0'), name='home'),
    url(r'^article/add$', 'main.views.add_article', name='addarticle'),
    url(r'^article/edit/(?P<article_id>\d+)$', 'main.views.edit_article', name='editarticle'),
    url(r'^articles/(?P<page_type>tags|subjects|search|recent)/(?P<item_name>[A-Za-z0-9_\-\.&% ]+)$', 'main.views.main', name='main'),
    url(r'^articles/(?P<page_type>tags|subjects|search|recent)/(?P<item_name>[A-Za-z0-9_\-\.&% ]+)/(?P<page>\d+)/(?P<delta>\d+)$', 'main.views.main', name='main'),
    url(r'^articles/blog/(?P<article_id>\d+)$', 'main.views.blog', name='blog'),
    url(r'^article/preview/(?P<article_id>\d+)$', 'main.views.preview_article', name='previewarticle'),
    url(r'^comments/answer_to/(?P<comment_id>\d+)$', 'main.views.comment_dialog', name='commentdialog'),
    url(r'^comments/edit/(?P<comment_id>\d+)$', 'main.views.edit_comment', name='editcomment'),

    url(r'^subject$', 'main.views.subjects', name='subjects'),
    url(r'^about$', 'main.views.about', name='about'),
    url(r'^links$', 'main.views.links', name='links'),

    url(r'^accounts/login/$', 'main.login_views.login_user', name='login'),
    url(r'^login$', 'main.login_views.login_user', name='login'),
    url(r'^logout', 'main.login_views.logout_user', name='logout'),
    url(r'^captcha/', include('captcha.urls')),

    # url(r'^openshift/', include('openshift.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

handler404 = 'main.views.page_not_found'

urlpatterns += patterns('',
    (r'^dashboard/', include('dashboard.urls')),
)

urlpatterns += patterns('',
    (r'^tasks/', include('tasks.urls')),
)