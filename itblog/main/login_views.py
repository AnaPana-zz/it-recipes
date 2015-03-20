#coding: utf-8 
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        user = authenticate(username=request.POST['username'],
                            password=request.POST['password'])
        if form.is_valid():
            if user is not None:
                if user.is_active:
                    login(request, user)
                    current_url = request.GET.get('next', '/')
                    return redirect(current_url)
    else:
        form = AuthenticationForm()
    return render(request, 'main/base/login.html', { 'form' : form })


def logout_user(request):
    logout(request)
    current_url = request.GET.get('next', r'/')
    return redirect(current_url)