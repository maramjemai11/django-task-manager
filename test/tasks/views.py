from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Task
from .forms import TaskForm, UserRegisterForm
from rest_framework import viewsets, permissions, generics
from .serializers import TaskSerializer,RegisterSerializer
from django.contrib.auth.models import User

# Create your views here.

@login_required
def task_list(request):
    """
    Display all tasks for the logged-in user.
    Supports filtering by status and sorting.
    """
    tasks = Task.objects.filter(user=request.user)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Sort by different criteria
    sort_by = request.GET.get('sort', '-created_date')
    if sort_by in ['title', '-title', 'due_date', '-due_date', 'priority', '-priority', 'created_date', '-created_date']:
        tasks = tasks.order_by(sort_by)
    
    # Calculate statistics
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()
    
    context = {
        'tasks': tasks,
        'status_choices': Task.STATUS_CHOICES,
        'current_status': status_filter,
        'current_sort': sort_by,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'tasks/task_list.html', context)

@login_required
def task_create(request):
    """
    Create a new task for the logged-in user.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'title': 'Create New Task'
    }
    return render(request, 'tasks/task_form.html', context)

@login_required
def task_update(request, pk):
    """
    Update an existing task.
    Only the task owner can edit their tasks.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'title': 'Edit Task'
    }
    return render(request, 'tasks/task_form.html', context)

@login_required
def task_delete(request, pk):
    """
    Delete a task.
    Only the task owner can delete their tasks.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('tasks:task_list')
    
    context = {
        'task': task
    }
    return render(request, 'tasks/task_confirm_delete.html', context)

@login_required
def task_toggle_complete(request, pk):
    """
    Toggle task completion status.
    Updates the completed_date when marking as completed.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if task.status == 'completed':
        task.status = 'pending'
        task.completed_date = None
        message = 'Task marked as pending'
    else:
        task.status = 'completed'
        task.completed_date = timezone.now()
        message = 'Task marked as completed'
    
    task.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': task.status,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('tasks:task_list')

@login_required
def task_detail(request, pk):
    """
    Display detailed information about a specific task.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    context = {
        'task': task
    }
    return render(request, 'tasks/task_detail.html', context)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return tasks for the logged-in user
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set the user to the logged-in user on creation
        serializer.save(user=self.request.user)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []  # Allow any user (authenticated or not) to access this view

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})
