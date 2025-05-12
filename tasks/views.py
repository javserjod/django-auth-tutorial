from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:   # check if passwords match
            # then register the user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Username already exists'})
        else:
            return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Passwords do not match'})

@login_required
def tasks(request):   # only pending tasks
    tasks = Task.objects.filter(user = request.user, completed__isnull = True)  # filter by current user too
    return render(request, 'tasks.html', {'tasks': tasks, 'page_h1': 'Tasks Pending'})

@login_required
def tasks_completed(request):   # only completed tasks
    tasks = Task.objects.filter(user = request.user, completed__isnull = False).order_by('-completed')  # filter by current user too
    return render(request, 'tasks.html', {'tasks': tasks, 'page_h1': 'Tasks Completed'})


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm()})   # pass the form to the template
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)  # don't save yet (error, user missing)
            new_task.user = request.user  # set the user to the logged in user
            new_task.save() # save the task to the database
            return redirect('tasks')   # pass the form to the template
        except ValueError:
            return render(request, 'create_task.html', {'form': TaskForm(), 'error': 'Bad data passed in. Try again.'})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk = task_id, user=request.user) # get task if it belongs to user
    if request.method =="GET":
        form = TaskForm(instance=task)  # pass form with current task data
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            form = TaskForm(request.POST, instance = task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task'})

@login_required            
def task_complete(request, task_id):
    task = get_object_or_404(Task, pk = task_id, user=request.user) # get task if it belongs to user
    if request.method == "POST":
        task.completed = timezone.now()  # set the completed time to now
        task.save()
        return redirect('tasks')

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk = task_id, user=request.user) # get task if it belongs to user
    if request.method == "POST":
        task.delete()
        return redirect('tasks')


@login_required
def signout(request):    #different name to avoid confusion with logout
    logout(request)
    return redirect('home')


def signin(request):  # different name to avoid confusion with login
    if request.method=="GET":
        return render(request, 'signin.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm(), 'error': 'Username and password do not match'})
        else:
            login(request, user)
            return redirect('tasks')
        
