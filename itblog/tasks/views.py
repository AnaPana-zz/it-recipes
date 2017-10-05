#coding: utf-8 
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import *
from .models import *
from main.utils import get_query, get_pagination_info, refresh_captcha, send_mail


def main(request, page_type, item_name, page=1, delta=10, **kwargs):
    context_dict = {}
    context_dict['tags'] = TaskTag.objects.all().order_by('name')
    context_dict['list'] = get_subjects_tree()
    context_dict['page_type'] = page_type
    context_dict['item_name'] = item_name
    
    # subjects_results, tag_results, search_results, all_results
    return globals()[page_type + '_results'](request, context_dict,
                                             item_name=item_name,
                                             page=int(page),
                                             delta=int(delta))


def all_results(request, context_dict, **kwargs):
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    tasks = Task.objects.all()
    context_dict['tasks'] = tasks[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(tasks), p, delta)
    return render(request, 'tasks/tasks.html', context_dict)


def tags_results(request, context_dict, **kwargs):
    tag_name = str(kwargs.get('item_name'))
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    tasks = TaskTag.objects.get(name=tag_name).task_set.select_related('subject')
                                                
    context_dict['tasks'] = tasks[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(tasks), p, delta)
    return render(request, 'tasks/tasks.html', context_dict)


def subjects_results(request, context_dict, **kwargs):
    subject_name = str(kwargs.get('item_name'))
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    tasks = Task.objects.filter(subject__name=subject_name)\
                                                    .select_related()
    context_dict['tasks'] = tasks[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(tasks), p, delta)
    return render(request, 'tasks/tasks.html', context_dict)


def search_results(request, context_dict, **kwargs):
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    query_string = ''
    tasks = []
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['name', 'body'])
        
        tasks = Task.objects.filter(entry_query).order_by('-date')
        context_dict['query'] = request.GET['q']
    
    context_dict['tasks'] = tasks[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(tasks), p, delta)
    
    return render(request, 'tasks/tasks.html', context_dict)


def task(request, task_id):
    context_dict = {}
    context_dict['tags'] = TaskTag.objects.all().order_by('name')
    context_dict['list'] = get_subjects_tree()
    try:
        task = Task.objects.get(pk=int(task_id))
    except Task.DoesNotExist:
        return redirect('tasks', 'all', 0)
    
    if request.user.is_authenticated():
        form = SolutionForm(initial={'author': request.user,
                                     'task':task})
        form.fields['author_name'].widget = forms.HiddenInput()
    else:
        form = SolutionForm(initial={'task':task})

    if request.is_ajax() and 'refresh_captcha' in request.GET:
        return refresh_captcha()
    
    if request.method == 'POST':
        if 'delete_request' in request.POST:
            if request.POST['type'] == 'task':
                task.delete()
                return HttpResponse("")
            elif request.POST['type'] == 'solution':
                solution = Solution.objects.get(pk=int(request.POST['item_id']))
                solution.delete()
                return HttpResponse("")
            elif request.POST['type'] == 'solution comment':
                comment = SolutionComment.objects.get(pk=int(request.POST['item_id']))
                comment.delete()
                return HttpResponse("")
        elif 'vote_request' in request.POST:
            if request.POST['type'] == 'task':
                task = Task.objects.get(pk=int(request.POST['item_id']))
                task.votes += int(request.POST['value'])
                task.save()
                return HttpResponse("")
            elif request.POST['type'] == 'solution':
                solution = Solution.objects.get(pk=int(request.POST['item_id']))
                solution.votes += int(request.POST['value'])
                solution.save()
                return HttpResponse("")
        else:
            form = SolutionForm(request.POST)
            if form.is_valid():
                solution = form.save()
                message_subject = 'New solution has been added for your task \"%s\"' \
                                                                % task.name
                message_body = "User %s has added a new solution to your task." +\
                "\nGo here and view it:\nwww.it-recipes.com%s"
                a = solution.author if solution.author else solution.author_name 
                message_body = message_body % (a, request.get_full_path())
                
                send_mail(task.author.email, message_subject, message_body)
                return redirect('task', task.id)
            else:
                if request.user.is_authenticated():
                    form.fields['author_name'].widget = forms.HiddenInput()
    
    context_dict['form'] = form
    context_dict['task'] = task
    solutions = []
    user_can_view_solutions = any([s.author == request.user \
                                  for s in Solution.objects.filter(task=task)])
    context_dict['user_can_view_solutions'] = user_can_view_solutions
    
    for s in Solution.objects.filter(task=task).order_by('-votes'):
        solutions.append({'solution' : s,
                          'comments' : SolutionComment.objects.filter(
                                                        solution=s).order_by('-date')
                          })
    context_dict['solutions'] = solutions
    
    return render(request, 'tasks/task.html', context_dict)


def add_solution_comment(request, solution_id):
    solution = Solution.objects.get(id=int(solution_id))
    task = Task.objects.get(solution=solution)

    if request.is_ajax() and 'refresh_captcha' in request.GET:
        return refresh_captcha()

    if request.user.is_authenticated():
        form = SolutionCommentForm(initial={'author': request.user,
                                     'solution':solution})
        form.fields['author_name'].widget = forms.HiddenInput()
    else:
        form = SolutionCommentForm(initial={'solution':solution})
    
    if request.method == 'POST':
        form = SolutionCommentForm(request.POST)
        if request.user.is_authenticated():
            form.fields['author_name'].widget = forms.HiddenInput()
        
        if form.is_valid():
            comment = form.save()
            message_subject = 'New comment has been added to your solution for task \"%s\"' \
                                                                % task.name
            message_body = "User %s has added a new comment to your solution." +\
            "\nGo here and view it:\nwww.it-recipes.com%s"
            a = comment.author if comment.author else comment.author_name 
            url_link = str(reverse('tasks.views.task', args=(task.id, )))
            message_body = message_body % (a, url_link)
            
            send_mail(solution.author.email, message_subject, message_body)
            return redirect('task', task.id)
    
    return render(request, 'tasks/solutioncomment.html', {'form' : form,
                                                                      'task_id' : task.id,
                                                                      })


def edit_solution_comment(request, comment_id):

    if request.is_ajax() and 'refresh_captcha' in request.GET:
        return refresh_captcha()

    try:
        comment = SolutionComment.objects.get(id=int(comment_id))
        task_id = comment.solution.task.id
    except SolutionComment.DoesNotExist:
        return redirect('task', task_id)

    form = SolutionCommentForm(instance=comment)
    if request.user.is_authenticated():
                form.fields['author_name'].widget = forms.HiddenInput()

    if request.method == 'POST':
        form = SolutionCommentForm(request.POST, instance=comment)
        if request.user.is_authenticated():
            form.fields['author_name'].widget = forms.HiddenInput()
            if form.is_valid():
                comment = form.save()
                message_subject = 'Comment to your solution has been edited'
                message_body = "User %s has edited comment to your solution." +\
                "\nGo here and view it:\nwww.it-recipes.com%s"
                a = comment.author if comment.author else comment.author_name 
                url_link = str(reverse('tasks.views.task', args=(task.id, )))
            
                message_body = message_body % (a, url_link)
                
                send_mail(comment.solution.author.email, message_subject, message_body)
                return redirect('task', task_id)
    
    return render(request, 'tasks/solutioncomment.html', {'form' : form,
                                                                      'task_id' : task_id,
                                                                      })


def get_subjects_tree():
    subjects_list = []
    for parent in TaskSubject.objects.filter(parent_subject=None).select_related('parent_subject'):
        children = []
        for subject in TaskSubject.objects.filter(parent_subject=parent):
            tasks = Task.objects.filter(subject=subject).order_by('-pk').values()
            children.append({'subject' : subject,
                             'count' : len(tasks),
                             'tasks' : tasks})
        subjects_list.append({'parent_subject' : parent, 'children' : children})
    return subjects_list


@login_required
def subjects(request):
    """
    Is responsible for 'Subjects manager'
    """
    result = []
    for subject in TaskSubject.objects.filter(parent_subject=None):
        result.append({
                'parent' : subject,
                'children' : TaskSubject.objects.filter(parent_subject=subject)})
    
    if request.method == 'POST':
        # add subject
        if not request.POST.get('item_id'):
            form = TaskSubjectForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('tasksubjects')
        
        # edit subject
        elif request.POST.get('edit_request'):
            subject = TaskSubject.objects.get(pk=int(request.POST['item_id']))
            form = TaskSubjectForm(initial={'author': request.user},
                                   instance=subject)
            return render(request,
                                      'main/forms/rowform.html',
                                      {
                                       'form' : form ,
                                       'item_id' : subject.id
                                       })
        
        elif request.POST.get('edit_submit'):
            form = TaskSubjectForm(request.POST,
                                   instance=TaskSubject.objects.get(
                                                    pk=request.POST['item_id']))
            if form.is_valid():
                form.save()
                return HttpResponse("")
            else:
                return render(request,
                                          'main/forms/rowform.html',
                                          {
                                           'form' : form ,
                                           'item_id' : request.POST['item_id']
                                           })
        
        # delete subject
        elif request.POST.get('delete_request'): 
            subject = TaskSubject.objects.get(pk=int(request.POST['item_id']))
            subject.delete()
            return HttpResponse('')
    # empty form
    else:
        form = TaskSubjectForm(initial={'author': request.user})
    return render(request, 'main/base/subjects.html',
                              {
                               'page_title' : 'Tasks subjects',
                               'result' : result,
                               'form' : form
                               })

@login_required
def add_task(request):

    if request.is_ajax() and 'refresh_captcha' in request.GET:
        return refresh_captcha()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            return redirect('task', task.id)
    else:
        form = TaskForm(initial={'author' : request.user.id})
    tags = ",".join(list(set(["\'%s\'" % t.name for t in TaskTag.objects.all()])))
    return render(request, 'tasks/addtask.html', {'tags' : tags,
                                                              'form' : form})


@login_required
def edit_task(request, task_id):

    if request.is_ajax() and 'refresh_captcha' in request.GET:
        return refresh_captcha()

    task = Task.objects.get(pk=int(task_id))
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect('task', task.id)
    else:
        form = TaskForm(instance=task, 
                        initial={
                        'mtags' : ','.join([t.name for t in task.tags.all()])
                        })
    tags = ",".join(list(set(["\'%s\'" % t.name for t in TaskTag.objects.all()])))
    return render(request, 'tasks/addtask.html',
                                                        {'form' : form,
                                                         'tags' : tags,
                                                         'task_id' : task.id})


@login_required
def edit_solution(request, solution_id):

    if request.is_ajax() and 'refresh_captcha' in request.GET:
        return refresh_captcha()

    solution = Solution.objects.get(pk=int(solution_id))
    if request.method == "POST":
        form = SolutionForm(request.POST, instance=solution)
        if form.is_valid():
            solution = form.save()
            return redirect('task', solution.task.id)
    else:
        form = SolutionForm(instance=solution)
    form.fields['author_name'].widget = forms.HiddenInput()
    return render(request, 'tasks/solutioncomment.html',
                                                        {'form' : form,
                                                         'task_id' : solution.task.id})
