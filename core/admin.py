import datetime

# Register Models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Q
from django.db.models import Sum, Count
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from .models import User, Client, Project, Task, Income, Expense, Invoice

# Customize Admin Header
admin.site.site_header = "TitansManager Admin"
admin.site.site_title = "TitansManager Admin Portal"
admin.site.index_title = "Welcome to TitansManager Admin"

# Inline for Tasks
class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'full_name',
        'email',
        'employee_id',
        'display_status',
        'department',
        'role',
        'display_workload',
        'display_reports_to',
    )

    list_filter = (
        'status',
        'role',
        'department',
        'is_active',
        ('hire_date', DateRangeFilter),
        ('last_login', DateRangeFilter),
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'employee_id',
        'phone',
    )

    fieldsets = (
        ('Personal Information', {
            'fields': (
                ('username', 'email'),
                ('first_name', 'last_name'),
                ('password',),
            )
        }),
        ('Work Information', {
            'fields': (
                ('role', 'department', 'status'),
                'employee_id',
                'job_title',
                'reports_to',
                'hire_date',
                'hourly_rate',
            )
        }),
        ('Contact Details', {
            'fields': (
                'phone',
                ('emergency_contact', 'emergency_phone'),
            )
        }),
        ('Skills & Expertise', {
            'fields': (
                'skills',
                'certifications',
            ),
            'classes': ('collapse',)
        }),
        ('Work Schedule', {
            'fields': (
                'working_hours',
                'time_zone',
            ),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': (
                'last_login',
                'date_joined',
                'last_password_change',
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = (
        'last_login',
        'date_joined',
        'last_password_change',
    )

    def display_status(self, obj):
        colors = {
            'active': 'green',
            'on_leave': 'orange',
            'inactive': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    display_status.short_description = 'Status'

    def display_workload(self, obj):
        active_tasks = obj.tasks.exclude(status='Completed').count()
        total_tasks = obj.tasks.count()
        if total_tasks:
            return format_html(
                '{} active / {} total',
                active_tasks,
                total_tasks
            )
        return '0 tasks'

    display_workload.short_description = 'Workload'

    def display_reports_to(self, obj):
        if obj.reports_to:
            return format_html(
                '<a href="{}/">{}</a>',
                obj.reports_to.id,
                obj.reports_to.get_full_name() or obj.reports_to.username
            )
        return '-'

    display_reports_to.short_description = 'Reports To'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reports_to')

    actions = ['mark_as_active', 'mark_as_inactive', 'mark_as_on_leave']

    def mark_as_active(self, request, queryset):
        queryset.update(status='active', is_active=True)

    mark_as_active.short_description = "Mark selected users as active"

    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive', is_active=False)

    mark_as_inactive.short_description = "Mark selected users as inactive"

    def mark_as_on_leave(self, request, queryset):
        queryset.update(status='on_leave')

    mark_as_on_leave.short_description = "Mark selected users as on leave"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_users': queryset.count(),
            'active_users': queryset.filter(status='active').count(),
            'department_counts': dict(
                queryset.values('department')
                .annotate(count=Count('id'))
                .values_list('department', 'count')
            ),
            'role_counts': dict(
                queryset.values('role')
                .annotate(count=Count('id'))
                .values_list('role', 'count')
            )
        }

        response.context_data['summary_metrics'] = metrics
        return response


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'company',
        'email',
        'display_status',
        'display_projects',
        'display_revenue',
        'display_outstanding',
        'created_at'
    )

    list_filter = (
        'status',
        'industry',
        'country',
        ('created_at', DateRangeFilter),
    )

    search_fields = (
        'name',
        'email',
        'company',
        'phone',
        'address',
        'city',
        'tax_number'
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'company',
                'status',
                'industry',
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                'alternate_email',
                'phone',
                'mobile_phone',
                'website',
            )
        }),
        ('Address Information', {
            'fields': (
                'address',
                'city',
                'state',
                'postal_code',
                'country',
            )
        }),
        ('Billing Information', {
            'fields': (
                'billing_address',
                'billing_email',
                'payment_terms',
                'tax_number',
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def display_status(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'red',
            'prospect': 'blue',
            'former': 'grey'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    display_status.short_description = 'Status'

    def display_projects(self, obj):
        return format_html(
            '<a href="?client__id__exact={}">{} projects</a>',
            obj.id,
            obj.total_projects
        )

    display_projects.short_description = 'Projects'

    def display_revenue(self, obj):
        return f"${obj.total_revenue:,.2f}"

    display_revenue.short_description = 'Total Revenue'

    def display_outstanding(self, obj):
        if obj.total_outstanding > 0:
            return format_html(
                '<span style="color: red;">${:,.2f}</span>',
                obj.total_outstanding
            )
        return "$0.00"

    display_outstanding.short_description = 'Outstanding'

    actions = ['mark_as_active', 'mark_as_inactive']

    def mark_as_active(self, request, queryset):
        queryset.update(status='active')

    mark_as_active.short_description = "Mark selected clients as active"

    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')

    mark_as_inactive.short_description = "Mark selected clients as inactive"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # Add summary metrics
        metrics = {
            'total_clients': queryset.count(),
            'active_clients': queryset.filter(status='active').count(),
            'total_revenue': queryset.aggregate(
                total=Sum('incomes__amount'))['total'] or 0,
            'total_outstanding': queryset.aggregate(
                total=Sum('invoices__amount',
                          filter=Q(invoices__status='Unpaid')))['total'] or 0
        }

        response.context_data['summary_metrics'] = metrics
        return response



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'client',
        'display_status',
        'manager',
        'display_dates',
        'display_budget',
        'display_completion',
        'display_profit',
    )

    list_filter = (
        'status',
        'priority',
        'client',
        ('start_date', DateRangeFilter),
        ('end_date', DateRangeFilter),
    )

    search_fields = (
        'code',
        'name',
        'client__name',
        'description',
        'manager__username',
    )

    inlines = [TaskInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('code', 'name'),
                'description',
                ('status', 'priority'),
                'client',
                'manager',
            )
        }),
        ('Dates', {
            'fields': (
                ('start_date', 'end_date'),
                ('actual_start_date', 'actual_end_date'),
            )
        }),
        ('Financial Information', {
            'fields': (
                'budget',
                'actual_cost',
                ('hourly_rate', 'estimated_hours'),
            )
        }),
        ('Team', {
            'fields': ('team_members',),
        }),
        ('Additional Information', {
            'fields': (
                'github_repo',
                'documentation_url',
                'notes',
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('code', 'created_at', 'updated_at')
    filter_horizontal = ('team_members',)

    def display_status(self, obj):
        colors = {
            'planning': 'blue',
            'in_progress': 'orange',
            'on_hold': 'red',
            'completed': 'green',
            'cancelled': 'grey'
        }
        if obj.is_overdue:
            return format_html(
                '<span style="color: red;">⚠️ {}</span>',
                obj.get_status_display()
            )
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    display_status.short_description = 'Status'

    def display_dates(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="color: red;">{} to {}</span>',
                obj.start_date.strftime('%Y-%m-%d'),
                obj.end_date.strftime('%Y-%m-%d')
            )
        return f"{obj.start_date.strftime('%Y-%m-%d')} to {obj.end_date.strftime('%Y-%m-%d')}"

    display_dates.short_description = 'Timeline'

    def display_budget(self, obj):
        percentage = obj.budget_utilized
        color = 'green' if percentage <= 100 else 'red'
        return format_html(
            '${:,.2f} <span style="color: {};">({:.1f}%)</span>',
            obj.budget,
            color,
            percentage
        )

    display_budget.short_description = 'Budget'

    def display_completion(self, obj):
        percentage = obj.completion_percentage
        return format_html(
            '<div style="width: 100px; background-color: #f1f1f1;">'
            '<div style="width: {}px; background-color: #4CAF50; height: 20px;">'
            '</div></div> {:.1f}%',
            percentage,
            percentage
        )

    display_completion.short_description = 'Completion'

    def display_profit(self, obj):
        profit = obj.total_income - obj.total_expenses
        color = 'green' if profit >= 0 else 'red'
        return format_html(
            '<span style="color: {};">${:,.2f}</span>',
            color,
            profit
        )

    display_profit.short_description = 'Profit/Loss'

    actions = ['mark_as_completed', 'mark_as_on_hold']

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed', actual_end_date=timezone.now().date())

    mark_as_completed.short_description = "Mark selected projects as completed"

    def mark_as_on_hold(self, request, queryset):
        queryset.update(status='on_hold')

    mark_as_on_hold.short_description = "Mark selected projects as on hold"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_projects': queryset.count(),
            'active_projects': queryset.filter(status='in_progress').count(),
            'total_budget': queryset.aggregate(total=Sum('budget'))['total'] or 0,
            'total_profit': queryset.aggregate(
                profit=Sum('incomes__amount') - Sum('expenses__amount')
            )['profit'] or 0
        }

        response.context_data['summary_metrics'] = metrics
        return response



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'display_status',
        'project',
        'assigned_to',
        'priority',
        'display_due_date',
        'display_time_tracking',
        'display_completion',
    )

    list_filter = (
        'status',
        'priority',
        'task_type',
        'project',
        'assigned_to',
        ('due_date', DateRangeFilter),
        ('created_at', DateRangeFilter),
    )

    search_fields = (
        'name',
        'description',
        'project__name',
        'assigned_to__username',
        'tags',
    )

    raw_id_fields = ('project', 'assigned_to', 'reviewer')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'description',
                'project',
                ('status', 'priority', 'task_type'),
            )
        }),
        ('Assignment', {
            'fields': (
                'assigned_to',
                'reviewer',
                'dependencies',
            )
        }),
        ('Timing', {
            'fields': (
                'due_date',
                ('estimated_hours', 'actual_hours'),
                ('started_at', 'completed_at'),
            )
        }),
        ('Additional Information', {
            'fields': (
                'github_issue',
                'tags',
                'notes',
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'started_at', 'completed_at')
    filter_horizontal = ('dependencies',)

    def display_status(self, obj):
        colors = {
            'pending': '#FFA500',  # Orange
            'in_progress': '#1E90FF',  # Blue
            'review': '#9370DB',  # Purple
            'completed': '#32CD32',  # Green
            'blocked': '#DC143C',  # Red
            'cancelled': '#808080'  # Grey
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    display_status.short_description = 'Status'

    def display_due_date(self, obj):
        if obj.is_overdue:
            days_overdue = (timezone.now().date() - obj.due_date).days
            return format_html(
                '<span style="color: red;">⚠️ {} ({} days overdue)</span>',
                obj.due_date.strftime('%Y-%m-%d'),
                days_overdue
            )
        return obj.due_date.strftime('%Y-%m-%d')

    display_due_date.short_description = 'Due Date'

    def display_time_tracking(self, obj):
        if obj.estimated_hours > 0:
            percentage = (obj.actual_hours / obj.estimated_hours) * 100
            color = 'green' if percentage <= 100 else 'red'
            return format_html(
                '{:.1f}h / {:.1f}h <span style="color: {};">({:.0f}%)</span>',
                obj.actual_hours,
                obj.estimated_hours,
                color,
                percentage
            )
        return f"{obj.actual_hours}h"

    display_time_tracking.short_description = 'Time Spent'

    def display_completion(self, obj):
        percentage = obj.completion_percentage
        return format_html(
            '<div style="width: 100px; background-color: #f1f1f1;">'
            '<div style="width: {}px; background-color: #4CAF50; height: 20px;">'
            '</div></div> {:.1f}%',
            percentage,
            percentage
        )

    display_completion.short_description = 'Completion'

    actions = ['mark_as_in_progress', 'mark_as_completed', 'mark_as_blocked']

    def mark_as_in_progress(self, request, queryset):
        queryset.filter(status='pending').update(
            status='in_progress',
            started_at=timezone.now()
        )

    mark_as_in_progress.short_description = "Mark selected tasks as in progress"

    def mark_as_completed(self, request, queryset):
        queryset.update(
            status='completed',
            completed_at=timezone.now()
        )

    mark_as_completed.short_description = "Mark selected tasks as completed"

    def mark_as_blocked(self, request, queryset):
        queryset.update(status='blocked')

    mark_as_blocked.short_description = "Mark selected tasks as blocked"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'project', 'assigned_to', 'reviewer'
        )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new task
            if not obj.assigned_to:
                obj.assigned_to = request.user
        super().save_model(request, obj, form, change)


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('display_amount', 'client', 'project', 'income_type',
                    'date', 'status', 'payment_method', 'display_overdue')

    list_filter = (
        'status',
        'income_type',
        'payment_method',
        ('date', DateRangeFilter),
        'client',
        'project'
    )

    search_fields = (
        'client__name',
        'project__name',
        'payment_reference',
        'description'
    )

    readonly_fields = ('created_at', 'updated_at', 'tax_amount', 'total_amount')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'client', 'project', 'income_type', 'amount', 'description'
            )
        }),
        ('Dates', {
            'fields': (
                'date', 'expected_date', 'received_date'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method', 'payment_reference', 'status', 'invoice'
            )
        }),
        ('Tax Information', {
            'fields': (
                'tax_rate', 'tax_amount'
            )
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def display_amount(self, obj):
        return f"${obj.amount:,.2f}"

    display_amount.short_description = 'Amount'
    display_amount.admin_order_field = 'amount'

    def display_overdue(self, obj):
        if obj.is_overdue:
            return f"⚠️ {obj.days_overdue} days"
        return "✓"

    display_overdue.short_description = 'Overdue'

    actions = ['mark_as_received', 'mark_as_pending']

    def mark_as_received(self, request, queryset):
        queryset.update(
            status='received',
            received_date=datetime.date.today()
        )

    mark_as_received.short_description = "Mark selected incomes as received"

    def mark_as_pending(self, request, queryset):
        queryset.update(
            status='pending',
            received_date=None
        )

    mark_as_pending.short_description = "Mark selected incomes as pending"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_income': queryset.aggregate(
                total=Sum('amount'))['total'] or 0,
            'pending_income': queryset.filter(
                status='pending').aggregate(
                total=Sum('amount'))['total'] or 0,
            'received_income': queryset.filter(
                status='received').aggregate(
                total=Sum('amount'))['total'] or 0
        }

        response.context_data['summary_metrics'] = metrics
        return response


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'display_total', 'date',
                    'status', 'is_recurring', 'receipt_link')
    list_filter = (
        'status',
        'category',
        'payment_method',
        'is_recurring',
        ('date', DateRangeFilter),
        'tax_status',
    )
    search_fields = ('title', 'description', 'vendor', 'invoice_number')
    readonly_fields = ('created_at', 'updated_at', 'total_amount')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'amount', 'tax_amount', 'category')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_reference', 'tax_status',
                       'date', 'due_date', 'paid_date')
        }),
        ('Recurring Settings', {
            'fields': ('is_recurring', 'recurring_frequency', 'recurring_end_date'),
            'classes': ('collapse',)
        }),
        ('Documentation', {
            'fields': ('receipt', 'invoice_number', 'vendor', 'vendor_tax_number')
        }),
        ('Approval Information', {
            'fields': ('status', 'submitted_by', 'approved_by', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_total(self, obj):
        return f"${obj.total_amount:.2f}"

    display_total.short_description = 'Total Amount'

    def receipt_link(self, obj):
        if obj.receipt:
            return format_html('<a href="{}" target="_blank">View Receipt</a>',
                               obj.receipt.url)
        return "No receipt"

    receipt_link.short_description = 'Receipt'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('submitted_by', 'approved_by')

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new expense
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['mark_as_approved', 'mark_as_paid']

    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved', approved_by=request.user)

    mark_as_approved.short_description = "Mark selected expenses as approved"

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid', paid_date=datetime.date.today())

    mark_as_paid.short_description = "Mark selected expenses as paid"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_amount': queryset.aggregate(
                total=Sum('amount') + Sum('tax_amount'))['total'] or 0,
            'pending_amount': queryset.filter(
                status='pending').aggregate(
                total=Sum('amount') + Sum('tax_amount'))['total'] or 0,
        }

        response.context_data['summary_metrics'] = metrics
        return response


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'client',
        'project',
        'display_amount',
        'display_status',
        'date',
        'due_date'
    )

    list_filter = (
        'status',
        'date',
        'client',
        'project',
    )

    search_fields = (
        'invoice_number',
        'client__name',
        'project__name',
        'notes',
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'invoice_number',
                ('client', 'project'),
                ('date', 'due_date'),
                'amount',
                'status',
                'notes',
            )
        }),
    )

    def display_amount(self, obj):
        return f"${obj.amount:,.2f}"

    display_amount.short_description = 'Amount'

    def display_status(self, obj):
        colors = {
            'draft': 'grey',
            'sent': 'blue',
            'paid': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    display_status.short_description = 'Status'

    actions = ['mark_as_paid', 'mark_as_sent']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')

    mark_as_paid.short_description = "Mark selected invoices as paid"

    def mark_as_sent(self, request, queryset):
        queryset.update(status='sent')

    mark_as_sent.short_description = "Mark selected invoices as sent"
