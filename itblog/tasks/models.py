from django.db import models
from django.contrib.auth.models import User
from main.models import Tag


class Entity(models.Model):
    
    class Meta:
        abstract = True
    
    author = models.ForeignKey(User, on_delete=models.SET(0))
    date = models.DateTimeField(auto_now=True)


class TaskSubject(Entity):
    
    name = models.CharField(max_length=100, unique=True)
    parent_subject = models.ForeignKey('self', blank=True, null=True, verbose_name='Parent subject')
    
    def __unicode__(self):
        return self.name


class TaskTag(Entity):
    
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    amount = models.PositiveIntegerField(default=0)
    
    def __unicode__(self):
        return self.name


class Task(Entity):
    
    name = models.CharField(max_length=50, unique=True)
    body = models.TextField()
    subject = models.ForeignKey(TaskSubject, on_delete=models.SET(0))
    tags = models.ManyToManyField(TaskTag)
    votes = models.IntegerField(null=True, default=0)
    
    @property
    def solutions(self):
        return Solution.objects.filter(task_id=self.id).select_related()
    
    def __unicode__(self):
        return self.name


class Solution(models.Model):
    
    author_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Name')
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET(0))
    body = models.TextField()
    task = models.ForeignKey(Task)
    votes = models.IntegerField(null=True, default=0)
    date = models.DateTimeField(auto_now=True)


class SolutionComment(models.Model):
    
    author_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Name')
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET(0))
    body = models.TextField(verbose_name='Comment')
    solution = models.ForeignKey(Solution)
    date = models.DateTimeField(auto_now=True)