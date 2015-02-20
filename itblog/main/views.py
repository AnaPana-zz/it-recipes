#coding: utf-8 
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDict
from django import forms

from .forms import *
from .models import *
from utils import get_query, get_pagination_info, \
                  send_mail, refresh_captcha, get_neighbors


import json

@login_required
def subjects(request):
    """
    Is responsible for 'Subjects manager'
    """
    result = []
    for subject in Subject.objects.filter(parent_subject=None):
        result.append({
                'parent' : subject,
                'children' : Subject.objects.filter(parent_subject=subject)})
    
    if request.method == 'POST':
        # add subject
        if not request.POST.get('item_id'):
            form = SubjectForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('subjects')
        
        # edit subject
        elif request.POST.get('edit_request'):
            subject = Subject.objects.get(pk=int(request.POST['item_id']))
            form = SubjectForm(instance=subject)
            return render(request,
                                      'main/forms/rowform.html',
                                      {
                                       'form' : form ,
                                       'item_id' : subject.id
                                       })
        
        elif request.POST.get('edit_submit'):
            form = SubjectForm(request.POST,
                               instance=Subject.objects.get(
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
            subject = Subject.objects.get(pk=int(request.POST['item_id']))
            subject.delete()
            return HttpResponse('')
    # empty form
    else:
        form = SubjectForm()
    return render(request, 'main/base/subjects.html',
                              {
                               'page_title' : 'Articles subjects',
                               'result' : result,
                               'form' : form
                               })


def main(request, page_type, item_name, page=1, delta=10, **kwargs):
    
    context_dict = {}
    context_dict['recent_articles'] = get_recent_articles()
    context_dict['tags'] = Tag.objects.all().filter(article__is_published=True)\
                                .distinct().order_by('name')
    context_dict['list'] = get_subjects_tree()
    context_dict['page_type'] = page_type
    context_dict['item_name'] = item_name
    
    # subjects_results, tag_results, search_results, recent_results
    return globals()[page_type + '_results'](request, context_dict,
                                             item_name=item_name,
                                             page=int(page),
                                             delta=int(delta))


def blog(request, article_id=0):
    
    context_dict = {}
    context_dict['recent_articles'] = get_recent_articles()
    context_dict['tags'] = Tag.objects.all().filter(article__is_published=True)\
                                .distinct().order_by('name')
    context_dict['list'] = get_subjects_tree()
    context_dict['query'] = request.GET.get('q', '')

    if not int(article_id):
        return redirect('main', 'recent', 0)
 
    try:
        article = Article.objects.get(pk=int(article_id), is_published=True)
        articles = list(Article.objects.filter(subject=article.subject,
                                           is_published=True).order_by('pk'))
         
        context_dict['previous'], context_dict['next'] = get_neighbors(article,
                                                                       articles)
    except Article.DoesNotExist:
        return redirect('main', 'recent', 0)

    context_dict['article'] = article
        
    if request.user.is_authenticated():
        form = CommentForm(initial={'author': request.user,
                                    'article':article,
                                    'parent_comment' : None})
        form.fields['name'].widget = forms.HiddenInput()
    else:
        form = CommentForm(initial={'article':article,
                                    'parent_comment' : None})
     
    if request.is_ajax() and 'refresh_captcha' in request.GET:
        return refresh_captcha()
     
    if request.method == 'POST':
        if request.POST.get('add_request'):
            if request.POST['type'] == 'favorites':
                Favorite.objects.create(owner=request.user, article=article)
        if request.POST.get('delete_request'):
            if request.POST['type'] == 'comment':
                comment = Comment.objects.get(pk=int(request.POST['item_id']))
                comment.delete()
            elif request.POST['type'] == 'article':
                article = Article.objects.get(pk=int(request.POST['item_id']))
                 
                for tag in article.mtags.all():
                    tag.amount -= 1
                    tag.save()
                 
                for img in ArticleImage.objects.filter(article=article):
                    _delete_image(img.id)
                 
                article.delete()
                return HttpResponse('Article was successfully deleted.')
            elif request.POST['type'] == 'favorite':
                favorite = Favorite.objects.get(article_id=article_id)
                favorite.delete()
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save()
                 
                message_subject = 'New comment for your article \"%s\"' \
                                                                % article.title
                message_body = "User %s has added a new comment to your post." +\
                "\nGo here and view it:\nwww.it-recipes.com%s" 
                message_body = message_body % (comment.author, request.get_full_path())
                 
                send_mail(article.author.email, message_subject, message_body)
                 
                return redirect('blog', article.id)
            else:
                if request.user.is_authenticated():
                    form.fields['name'].widget = forms.HiddenInput()
     
    context_dict['form'] = form
    context_dict['comments'] = get_comments_tree(article_id)
    
    return render(request, 'main/blog/blog.html', context_dict)


def edit_comment(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    form = CommentForm(instance=comment)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog', comment.article.id)
    if request.user.is_authenticated():
        form.fields['name'].widget = forms.HiddenInput()
    return render(request, 'main/blog/editcomment.html',
                    {
                     'comment' : comment,
                     'form' : form,
                     'cancel_link' : reverse('blog', args=(comment.article.id,))
                     })


def comment_dialog(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    if request.user.is_authenticated():
        form = CommentForm(initial={'author': request.user,
                                    'article':comment.article,
                                    'parent_comment' : comment})
    else:
        form = CommentForm(initial={'article':comment.article,
                                    'parent_comment' : comment})
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog', comment.article.id)
    if request.user.is_authenticated():
        form.fields['name'].widget = forms.HiddenInput()
    return render(request, 'main/blog/commentdialog.html',
                    {
                     'comment_dialog' : get_comment_dialog(comment_id),
                     'form' : form,
                     'cancel_link' : reverse('blog', args=(comment.article.id,))
                     })


def tags_results(request, context_dict, **kwargs):
    tag_name = str(kwargs.get('item_name'))
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    try:
        articles = Tag.objects.get(name=tag_name).article_set\
                                                    .filter(is_published=True)\
                                                    .select_related('subject')
    except Tag.DoesNotExist:
        articles = []
                                                
    context_dict['articles'] = articles[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(articles), p, delta)
    return render(request, 'main/itemresults/tagresults.html', context_dict)


def subjects_results(request, context_dict, **kwargs):
    subject_name = str(kwargs.get('item_name'))
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    articles = Article.objects.filter(subject__name=subject_name,
                                                    is_published=True)\
                                                    .select_related()
    context_dict['articles'] = articles[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(articles), p, delta)
    return render(request, 'main/itemresults/subjectresults.html', context_dict)


def search_results(request, context_dict, **kwargs):
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    query_string = ''
    articles = []
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['title', 'body'])
        
        articles = Article.objects.filter(entry_query)\
                            .filter(is_published=True).order_by('-date')
        context_dict['query'] = request.GET['q']
    
    context_dict['articles'] = articles[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(articles), p, delta)
    
    return render(request, 'main/itemresults/searchresults.html', context_dict)


def recent_results(request, context_dict, **kwargs):
    p = int(kwargs.get('page'))
    delta = int(kwargs.get('delta'))
    articles = Article.objects.filter(is_published=True).select_related()\
                                                        .order_by('-pk')
    context_dict['articles'] = articles[(p-1)*delta : p*delta]
    context_dict['pagination'] = get_pagination_info(len(articles), p, delta)
    return render(request, 'main/itemresults/subjectresults.html', context_dict)


@login_required
def add_article(request):
    if request.method == 'POST' and 'title' not in request.POST:
        return _image_function(request)
    
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            
            images = request.POST['article_images']
            _add_images_to_article(article, images)
            
            if request.POST['submit_type'] == 'publish':
                article.is_published = True
                article.save()
                return redirect('blog', article.id)
            elif request.POST['submit_type'] == 'draft':
                return redirect('editarticle', article.id)
            elif request.POST['submit_type'] == 'preview':
                return redirect('previewarticle', article.id)
    else:
        form = ArticleForm(initial={'author' : request.user.id})
    tags = ",".join(list(set(["\'%s\'" % t.name for t in Tag.objects.all()])))
    return render(request, 'main/blog/addarticle.html',
                                                              {
                                                               'form' : form,
                                                               'tags' : tags
                                                               })


@login_required
def edit_article(request, article_id):
    
    if request.method == 'POST' and 'title' not in request.POST:
        return _image_function(request)
    
    article = Article.objects.get(pk=int(article_id))
    article_images = ArticleImage.objects.filter(article=article)

    
    if request.user.is_superuser or \
        request.user.username == article.author.username:
        if request.method == "POST":
            
            if 'delete_request' in request.POST and request.POST['type'] == 'image':
                _delete_image(str(request.POST['item_id']))
            
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                article = form.save()
                
                images = request.POST['article_images']
                _add_images_to_article(article, images)
                
                if request.POST['submit_type'] == 'publish':
                    article.is_published = True
                    article.save()
                    return redirect('blog', article.id)
                elif request.POST['submit_type'] == 'draft':
                    article.is_published = False
                    article.save()
    
                    return redirect('editarticle', article.id)
                elif request.POST['submit_type'] == 'preview':
                    return redirect('previewarticle', article.id)
        else:
            form = ArticleForm(instance=article, initial={
                            'tags' : ','.join([t.name for t in article.mtags.all()])
                            })
    else:
        return redirect('blog', 0)
    tags = ",".join(list(set(["\'%s\'" % t.name for t in Tag.objects.all()])))
    return render(request, 'main/blog/editarticle.html',
                                                        {'form' : form,
                                                         'tags' : tags,
                                                         'article' : article,
                                                         'images' : article_images})


@login_required
def preview_article(request, article_id):
    article = Article.objects.get(pk=int(article_id))
    if request.method == "POST" and "publish_article" in request.POST:
        article.is_published = True
        article.save()
        return redirect('blog', article.id)
    return render(request, 'main/blog/previewarticle.html',
                                                      {
                                                       'page_title' : 'Preview',
                                                       'article' : article
                                                       })


def links(request):
    result = []
    for subject in Subject.objects.all():
        links = UsefulLink.objects.filter(subject=subject)
        if links:
            result.append({'subject' : subject,
                           'links' : links})
    # add link
    if request.method == 'POST' and "item_id" not in request.POST:
        form = UsefulLinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('links')

    # delete link
    elif 'delete_request' in request.POST: 
        link = UsefulLink.objects.get(pk=int(request.POST['item_id']))
        link.delete()
        return HttpResponse("")
    
    # empty form
    else:
        form = UsefulLinkForm()
    return render(request, 'main/base/links.html',
                                            {'page_title' : 'Useful links',
                                             'list' : result,
                                             'form' : form,
                                             'submit_title' : 'Save link',
                                             'cancel_title' : 'Cancel'
                                            })


def about(request):
    return render(request, 'main/base/about.html')


def get_recent_articles():
    return Article.objects.filter(is_published=True).order_by('-id')[:3]


def get_subjects_tree():
    subjects_list = []
    for parent in Subject.objects.filter(parent_subject=None).select_related('article'):
        children = []
        for subject in Subject.objects.filter(parent_subject=parent):
            articles = Article.objects.filter(subject=subject, is_published=True)\
                                                        .order_by('-pk').values()
            children.append({'subject' : subject,
                             'count' : len(articles),
                             'articles' : articles})
        subjects_list.append({'parent_subject' : parent, 'children' : children})
    return subjects_list


def get_comments_tree(article_id):
    result = []
    for parent in Comment.objects.filter(article_id=article_id,
                                                 parent_comment=None).order_by('date'):
        children = Comment.objects.filter(parent_comment=parent)
        result.append({'parent_comment' : parent,
                       'children' : children})
    return result


def get_comment_dialog(comment_id):
    comment = Comment.objects.get(pk=comment_id)
    return {'parent_comment' : comment,
            'children' : Comment.objects.filter(parent_comment=comment).values()}


def _image_function(request):
    if 'delete_request' in request.POST and request.POST['type'] == 'image':
        _delete_image(int(request.POST['item_id']))
    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        file = form.save()
        return HttpResponse(json.dumps({'id' : file.id,
                                              'url' : file.image.url,
                                              'name' : file.image.name}))
    elif form.errors:
        print form.errors
        return HttpResponse('')
    return HttpResponse('')

def _delete_image(id):
    file = ArticleImage.objects.get(pk=id)
    file.image.delete()
    file.delete()
    return HttpResponse('')

def _add_images_to_article(article, images):
    for img_id in images.split(','):
        if img_id:
            img = ArticleImage.objects.get(pk=str(img_id))
            img.article = article
            img.save()
            article.body += "<img src=%s style='width:100px'/><br/>" % img.image.url
            article.save()
