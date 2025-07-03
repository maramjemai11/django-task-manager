from django.contrib import admin
from .models import Task

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'due_date', 'created_date', 'is_overdue')
    list_filter = ('status', 'priority', 'created_date', 'due_date')
    search_fields = ('title', 'description')
    list_editable = ('status', 'priority')
    date_hierarchy = 'created_date'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('due_date', 'completed_date'),
            'classes': ('collapse',)
        }),
    )
