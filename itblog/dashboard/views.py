from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

from main.models import *
from tasks.models import Solution
from main.forms import PersonalForm

@login_required
def articles(request, page_type, subject_id):
    
    subject_id = int(subject_id)
    
    if page_type == 'articles':
        title = 'Articles'
        is_published = True
    elif page_type == 'drafts':
        title = 'Drafts'
        is_published = False
    
    articles = Article.objects.filter(author=request.user,
                                      is_published=is_published)\
                                      .order_by('subject')\
                                      .prefetch_related('mtags')\
                                      .select_related()
    
    if subject_id:
        articles = articles.filter(subject_id=subject_id)
    
    if request.POST:
        article = Article.objects.get(pk=int(request.POST['item_id']))
        if request.POST.get('delete_request'):
            article.delete()
        elif request.POST.get('publish_request'):
            article.is_published = True
            article.save()
    
    return render(request, 'dashboard/articles.html',
                      {
                       'title' : title,
                       'articles' : articles,
                       'subject_id': subject_id,
                       'subjects' : get_subjects(request, is_published=is_published),
                       'dashboard_amounts' : dashboard_amounts(request),
                       'page_type' : page_type
                       })


@login_required
def my_comments(request):
    comments = Comment.objects.filter(author=request.user)
    if request.POST.get('delete_request'):
        comment = Comment.objects.get(pk=int(request.POST['item_id']))
        comment.delete()
    return render(request, 'dashboard/mycomments.html',
                                                 {
                                                  'title' : 'My comments',
                                                  'comments' : comments
                                                 })


@login_required
def comments_to_me(request):
    comments = Comment.objects.filter(article__author=request.user)\
                                                .exclude(author=request.user)
    if request.POST.get('delete_request'):
        comment = Comment.objects.get(pk=int(request.POST['item_id']))
        comment.delete()
    return render(request, 'dashboard/commentstome.html',
                                                {
                                                 'title' : 'Comments to me',
                                                 'comments' : comments
                                                })


@login_required
def my_solutions(request):
    solutions = Solution.objects.filter(author=request.user).order_by('-date')
    if request.POST.get('delete_request'):
        solution = Solution.objects.get(pk=int(request.POST['item_id']))
        solution.delete()
    return render(request, 'dashboard/mysolutions.html',
                                                 {
                                                  'title' : 'My solutions',
                                                  'solutions' : solutions
                                                 })


@login_required
def favorites(request, page_type, subject_id):
    
    subject_id = int(subject_id)
    
    all_favorites = Favorite.objects.filter(owner=request.user)\
                                        .select_related('article__subject')\
                                        .select_related('article__subject__parent_subject')
    count = len(all_favorites)
    
    result = []
    for favorite in all_favorites:
        result.append({'parent_subject' : favorite.article.subject.parent_subject.name,
                       'subject' : favorite.article.subject})

    if subject_id:
        all_favorites = all_favorites.filter(article__subject__id=subject_id)

    if request.POST.get('delete_request'):
        if request.POST['type'] == 'favorite':
            favorite = Favorite.objects.get(article_id=int(request.POST['item_id']))
            favorite.delete()
    return render(request, 'dashboard/favorites.html',
                                                {
                                                 'all_items' : all_favorites,
                                                 'title' : 'Favorites',
                                                 'subjects' : result,
                                                 'subject_id' : subject_id,
                                                 'count' : count,
                                                 'page_type' : page_type
                                                })

@login_required
def private_settings(request, type):
    user = User.objects.get(pk=request.user.id)
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            user.username = request.POST['username']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            if request.POST['password1']:
                user.set_password(request.POST['password1'])
            user.save()
            return redirect('privatesettings', 'saved')
    else:
        form = PersonalForm(initial={'username' : user.username,
                                     'first_name' : user.first_name,
                                     'last_name' : user.last_name,
                                     'email' : user.email})
    return render(request, 'dashboard/privatesettings.html',
                              {'title' : 'Settings',
                               'form' : form,
                               'type' : type})



def get_subjects(request, is_published=False):
    result = []
    for article in Article.objects.filter(author=request.user,
                                          is_published=is_published)\
                                          .order_by('subject')\
                                          .select_related('subject')\
                                          .select_related('subject__parent_subject'):
        result.append({'parent_subject' : article.subject.parent_subject.name,
                       'subject' : article.subject})
    return result

def dashboard_amounts(request):
    return {
            'articles' : Article.objects.filter(author=request.user, is_published=True).count(),
            'drafts' : Article.objects.filter(author=request.user, is_published=False).count(),
            'my_comments' : Comment.objects.filter(author=request.user).count(),
            'comments_to_me' : Comment.objects.filter(article__author=request.user).exclude(author=request.user).count(),
            'solutions' : Solution.objects.filter(author=request.user).count(),
            'favorites' : Favorite.objects.filter(owner=request.user).count(),
            'settings' : ''}