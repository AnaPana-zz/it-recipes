from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', 'main.views.home', name='home'),
    url(r'^subject$', 'main.views.subjects', name='subjects'),
    url(r'^about$', 'main.views.about', name='about'),
    url(r'^links$', 'main.views.links', name='links'),

    url(r'^accounts/login/$', 'main.login_views.login_user', name='login'),
    url(r'^login$', 'main.login_views.login_user', name='login'),
    url(r'^logout', 'main.login_views.logout_user', name='logout'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
]

articles = [
    url(r'^(?P<page_type>tags|subjects|search|recent)/(?P<item_name>[A-Za-z0-9_\-\.&% ]+)$', 'main.views.main', name='main'),
    url(r'^(?P<page_type>tags|subjects|search|recent)/(?P<item_name>[A-Za-z0-9_\-\.&% ]+)/(?P<page>\d+)/(?P<delta>\d+)$', 'main.views.main', name='main'),
    url(r'^blog/(?P<article_id>\d+)$', 'main.views.blog', name='blog'),
]

article = [
    url(r'^add$', 'main.views.add_article', name='addarticle'),
    url(r'^edit/(?P<article_id>\d+)$', 'main.views.edit_article', name='editarticle'),
    url(r'^preview/(?P<article_id>\d+)$', 'main.views.preview_article', name='previewarticle'),
]

comments = [
    url(r'^answer_to/(?P<comment_id>\d+)$', 'main.views.comment_dialog', name='commentdialog'),
    url(r'^edit/(?P<comment_id>\d+)$', 'main.views.edit_comment', name='editcomment'),
]

urlpatterns += [
    (r'^articles/', include(articles)),
    (r'^article/', include(article)),
    (r'^comments/', include(comments)),
    (r'^dashboard/', include('dashboard.urls')),
    (r'^tasks/', include('tasks.urls')),
]