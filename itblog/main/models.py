from django.db import models
from django.contrib.auth.models import User

import os

def _get_upload_path(instance, filename):
    return filename
#     return os.path.join(instance.article.id, filename)


class Subject(models.Model):
    
    name = models.CharField(max_length=40, unique=True)
    parent_subject = models.ForeignKey('self', blank=True, null=True, verbose_name='Parent subject')
    
    def __unicode__(self):
        return self.name


class Tag(models.Model):
    
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.SET(None))
    amount = models.PositiveIntegerField(default=0)
    
    def __unicode__(self):
        return self.name


class Article(models.Model):
    
    author = models.ForeignKey(User, on_delete=models.SET(0))
    title = models.CharField(max_length=100, unique=True)
    body = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.SET(0))
    date = models.DateTimeField(auto_now=True)
#     tags = models.CharField(max_length=200)
    mtags = models.ManyToManyField(Tag)
    is_published = models.BooleanField(default=False)
    
    @property
    def tags_list(self):
        return self.tags.split(',')
    
    def is_in_favorites(self, user):
        return True if Favorite.objects.filter(article_id=self.id, owner=user) else False


class ArticleImage(models.Model):
    
    article = models.ForeignKey(Article, null=True, blank=True)
    image = models.ImageField(upload_to=_get_upload_path)


class UsefulLink(models.Model):
    
    url = models.URLField(max_length=300)
    description = models.CharField(max_length=100, blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET(0))
    
    def __unicode__(self):
        return self.url


class Comment(models.Model):
    
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Name')
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET('Undefined'))
    body = models.TextField(verbose_name='Comment')
    article = models.ForeignKey(Article)
    date = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', blank=True, null=True, verbose_name='Parent comment')


class Favorite(models.Model):
    
    class Meta:
        unique_together = ('owner', 'article')
    
    owner = models.ForeignKey(User)
    comment = models.TextField(verbose_name='Comment', blank=True, null=True)
    article = models.ForeignKey(Article)