#coding: utf-8 
from django import forms
from main.models import *
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from captcha.fields import CaptchaField


class ArticleForm(forms.ModelForm):
    
    tags = forms.CharField()
    
    class Meta:
        model = Article
        exclude = ('mtags',)
    
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['is_published'].widget = forms.HiddenInput()
        
        children_choices = lambda s: [(obj.id, obj.name) for obj in Subject.objects.filter(parent_subject=s)]  
        subject_choices = ((s.name, children_choices(s)) for s in Subject.objects.filter(parent_subject=None))
        self.fields['subject'].choices = subject_choices
        self.fields['tags'].help_text = "(write tag and press Space. You can use letters, digits, '.' , '_' and '-')"
        self.fields['tags'].widget.attrs['data-role'] = "tagsinput"
    
    def clean_tags(self):
        tags = self.cleaned_data['tags']
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
        tags = self.cleaned_data.get('tags')
        author = self.cleaned_data.get('author')
        cinstance = super(ArticleForm, self).save()
        for tag in cinstance.mtags.all():
            cinstance.mtags.remove(tag)
            tag.amount -= 1
            tag.save()
        for t in tags.split(','):
            try:
                tag = Tag.objects.get(name=t.lower())
            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=t.lower(), creator=author)
            finally:
                cinstance.mtags.add(tag)
                tag.amount += 1
                tag.save()
        cinstance.save()
        return cinstance


class ImageForm(forms.ModelForm):
    
    class Meta:
        model = ArticleImage
        fields = ('article', 'image', )

    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['article'].widget = forms.HiddenInput()


class SubjectForm(forms.ModelForm):
    
    class Meta:
        model = Subject
        fields = ('name', 'parent_subject', )
    
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'subject'
        self.fields['parent_subject'].queryset = Subject.objects.filter(parent_subject=None)


class UsefulLinkForm(forms.ModelForm):
    
    class Meta:
        model = UsefulLink
        fields = ('url', 'description', 'subject', )

    def __init__(self, *args, **kwargs):
        super(UsefulLinkForm, self).__init__(*args, **kwargs)
        
        children_choices = lambda s: [(obj.id, obj.name) for obj in Subject.objects.filter(parent_subject=s)]  
        subject_choices = ((s.name, children_choices(s)) for s in Subject.objects.filter(parent_subject=None))
        self.fields['subject'].choices = subject_choices


class CommentForm(forms.ModelForm):
    
    captcha = CaptchaField()
    
    class Meta:
        model = Comment
        fields = ('name', 'author', 'body',
                  'article', 'parent_comment')

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['article'].widget = forms.HiddenInput()
        self.fields['parent_comment'].widget = forms.HiddenInput()
        self.fields['body'].label = ''
        self.fields['name'].widget.attrs['class'] = 'input-xxlarge'
        self.fields['author'].widget = forms.HiddenInput()
        self.fields['captcha'].label = ''


class PersonalForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=60)
    last_name = forms.CharField(max_length=60)
    email = forms.EmailField()
    password1 = forms.CharField(max_length=60, widget=forms.PasswordInput(),
                                required=False, label="New password")
    password2 = forms.CharField(max_length=60, widget=forms.PasswordInput(),
                                required=False, label="Confirm new password")

    def clean(self):
        cleaned_data = super(PersonalForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
         
        if password1 or password2:
            if password1 != password2:
                self._errors['password2'] = self.error_class(["Passwords are not equal."])
            elif len(password2) < 6:
                self._errors['password2'] = self.error_class(["Password length must be at least 6 symbols."])
        return cleaned_data
        
        
# class UserForm(forms.ModelForm):
#      
#     class Meta:
#         model = User
