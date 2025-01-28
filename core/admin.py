from django.contrib import admin
from .models import User, Client, Project, Task, Income, Expense, Invoice

# Customize Admin Header
admin.site.site_header = "TitansManager Admin"
admin.site.site_title = "TitansManager Admin Portal"
admin.site.index_title = "Welcome to TitansManager Admin"

# Inline for Tasks
class TaskInline(admin.TabularInline):
    model = Task
    extra = 1

# Register Models
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    search_fields = ('username', 'email')
    list_filter = ('role',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company')
    search_fields = ('name', 'email', 'company')
    list_filter = ('company',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'start_date', 'end_date', 'budget')
    search_fields = ('name', 'client__name')
    list_filter = ('client', 'start_date', 'end_date')
    inlines = [TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'assigned_to', 'status', 'due_date')
    search_fields = ('name', 'project__name', 'assigned_to__username')
    list_filter = ('status', 'project', 'assigned_to')

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'client', 'project', 'invoice')
    search_fields = ('client__name', 'project__name')
    list_filter = ('date', 'client', 'project')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'category', 'project')
    search_fields = ('category', 'project__name')
    list_filter = ('category', 'date', 'project')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('client', 'project', 'amount', 'date', 'status')
    search_fields = ('client__name', 'project__name')
    list_filter = ('status', 'date', 'client')
