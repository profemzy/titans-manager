# core/admin/task_inline.py
from django.contrib import admin
from core.models import Task

class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
