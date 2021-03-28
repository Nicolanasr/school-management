from functools import reduce
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

def index(request):
    return redirect('index:login')

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('class:index')
    else:
        form = SignUpForm()
        ctx = {'form': form}
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                username = request.POST.get('username')
                password = request.POST.get('password1')
                username_f = form.cleaned_data['username']
                brk = True
                try:
                    User.objects.get(username__iexact=username)
                except:
                    brk = False
                if brk:
                    messages.warning(request, 'Username already in use')
                    return redirect('index:register')
                form.save()
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('index:index')
            else:
                err = form.errors.values()
                err = list(err)
                print(err)
                ctx = {'form': form, 'err': err}

        return render(request, 'index/register.html', ctx)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('class:index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                messages.error(request, 'Username or Password are incorrect')
                return render(request, 'index/login.html')


            user = authenticate(request, username=user, password=password)
            if user is not None:
                login(request, user)
                return redirect('class:index')
                # return redirect('index:index')
            else:
                print('Username or Password are incorrect')
                messages.error(request, 'Username or Password are incorrect')
                return render(request, 'index/login.html')

        return render(request, 'index/login.html')

def logoutPage(request):
    logout(request)
    return redirect('class:index')