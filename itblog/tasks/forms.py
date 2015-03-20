#coding: utf-8 
from django import forms
from tasks.models import *
from main.models import Tag
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from captcha.fields import CaptchaField

class TaskForm(forms.ModelForm):
    
    mtags = forms.CharField()
    
    class Meta:
        model = Task
        exclude = ('tags',)
    
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['author'].widget = forms.HiddenInput()
        
        children_choices = lambda s: [(obj.id, obj.name) for obj in TaskSubject.objects.filter(parent_subject=s)]  
        subject_choices = ((s.name, children_choices(s)) for s in TaskSubject.objects.filter(parent_subject=None))
        self.fields['subject'].choices = subject_choices
        self.fields['mtags'].label = ''
        self.fields['mtags'].help_text = "Write tag and press Space. You can use letters, digits, '.' , '_' and '-'."
        self.fields['mtags'].widget.attrs['data-role'] = "tagsinput"
        self.fields['body'].label = ''
        self.fields['votes'].widget = forms.HiddenInput()
    
    def clean_tags(self):
        tags = self.cleaned_data['mtags']
        if len(tags.split(',')) > 5:
            raise forms.ValidationError("Specify less than 6 tags!")
        else:
            invalid_tags = []
            for tag in tags.split(','):
                for l in tag:
                    if not (l.isdigit() or l.isalpha() or l in ['.', '-', '_']):
                        invalid_tags.append(tag)
                        break
            if invalid_tags:
                raise forms.ValidationError("These tags are invalid: %s" % ', '.join(invalid_tags))

        return tags
    
    def save(self):
        tags = self.cleaned_data.get('mtags')
        author = self.cleaned_data.get('author')
        cinstance = super(TaskForm, self).save()
        for tag in cinstance.tags.all():
            cinstance.tags.remove(tag)
            tag.amount -= 1
            tag.save()
        for t in tags.split(','):
            try:
                tag = TaskTag.objects.get(name=t.lower())
            except TaskTag.DoesNotExist:
                tag = TaskTag.objects.create(name=t.lower(), author=author)
            finally:
                cinstance.tags.add(tag)
                tag.amount += 1
                tag.save()
        cinstance.save()
        return cinstance

class TaskSubjectForm(forms.ModelForm):
    
    class Meta:
        model = TaskSubject
        fields = ('name', 'parent_subject')
    
    def __init__(self, *args, **kwargs):
        super(TaskSubjectForm, self).__init__(*args, **kwargs)
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['name'].widget.attrs['placeholder'] = 'subject'
        self.fields['parent_subject'].queryset = TaskSubject.objects.filter(parent_subject=None)


class SolutionForm(forms.ModelForm):
    
    captcha = CaptchaField()
    
    class Meta:
        model = Solution
        fields = ('author_name', 'author',
                  'body', 'task', 'votes')

    def __init__(self, *args, **kwargs):
        super(SolutionForm, self).__init__(*args, **kwargs)
        self.fields['author_name'].widget.attrs['class'] = 'input-xxlarge'
        self.fields['task'].widget = forms.HiddenInput()
        self.fields['body'].label = ''
        self.fields['author'].default = 0
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['captcha'].label = ''
        self.fields['votes'].widget = forms.HiddenInput()


class SolutionCommentForm(forms.ModelForm):
    
    captcha = CaptchaField()
    
    class Meta:
        model = SolutionComment
        fields = ('author_name', 'author',
                  'body', 'solution')

    def __init__(self, *args, **kwargs):
        super(SolutionCommentForm, self).__init__(*args, **kwargs)
        self.fields['author_name'].widget.attrs['class'] = 'input-xxlarge'
        self.fields['solution'].widget = forms.HiddenInput()
        self.fields['body'].label = ''
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['captcha'].label = ''