from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

urlpatterns = patterns('',
    url(r'^(?P<page_type>tags|subjects|search|all)/(?P<item_name>[A-Za-z0-9_\-\.&% ]+)$', 'tasks.views.main', name='tasks'),
    url(r'^(?P<page_type>tags|subjects|search|all)/(?P<item_name>[A-Za-z0-9_\-\.&% ]+)/(?P<page>\d+)/(?P<delta>\d+)$', 'tasks.views.main', name='tasks'),
    url(r'^subjects$', 'tasks.views.subjects', name='tasksubjects'),
    url(r'^(?P<task_id>\d+)$', 'tasks.views.task', name='task'),
    url(r'^add$', 'tasks.views.add_task', name='addtask'),
    url(r'^edit/(?P<task_id>\d+)$', 'tasks.views.edit_task', name='edittask'),
    url(r'^solution/edit/(?P<solution_id>\d+)$', 'tasks.views.edit_solution', name='editsolution'),
    url(r'^comment/(?P<solution_id>\d+)$', 'tasks.views.add_solution_comment', name='addsolutioncomment'),
    url(r'^comment/(?P<comment_id>\d+)/edit$', 'tasks.views.edit_solution_comment', name='editsolutioncomment'),
    )