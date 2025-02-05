from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from core.models import User
from core.admin.mixins import (
    StatusDisplayMixin,
    WorkloadDisplayMixin,
    ReportsToDisplayMixin,
    TimestampDisplayMixin,
    MetricsMixin
)


@admin.register(User)
class UserAdmin(StatusDisplayMixin, WorkloadDisplayMixin,
                ReportsToDisplayMixin, TimestampDisplayMixin,
                MetricsMixin, BaseUserAdmin):
    """
    Enhanced User admin interface using consolidated mixins for improved
    display and functionality while maintaining BaseUserAdmin features.
    """

    list_display = (
        'username',
        'email',
        'get_full_name',
        'employee_id',
        'department',
        'display_status',  # From StatusDisplayMixin
        'role',
        'display_workload',  # From WorkloadDisplayMixin
        'display_reports_to',  # From ReportsToDisplayMixin
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
        ('System Information', {
            'fields': (
                'date_joined',
                'last_login',
                'display_created_at',
                'display_updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = (
        'date_joined',
        'last_login',
        'display_created_at',
        'display_updated_at',
    )

    def get_metrics(self, queryset):
        """
        Override get_metrics to include user-specific metrics.
        """
        metrics = super().get_metrics(queryset)

        # Department breakdown
        dept_counts = dict(
            queryset.values('department')
            .annotate(count=Count('id'))
            .values_list('department', 'count')
        )

        # Role breakdown
        role_counts = dict(
            queryset.values('role')
            .annotate(count=Count('id'))
            .values_list('role', 'count')
        )

        # Task statistics
        task_metrics = {
            'users_with_tasks': queryset.filter(tasks__isnull=False)
            .distinct().count(),
            'total_active_tasks': queryset.filter(
                tasks__status__in=['planning', 'in_progress']
            ).count(),
            'overdue_tasks': queryset.filter(
                tasks__status__in=['planning', 'in_progress'],
                tasks__due_date__lt=timezone.now().date()
            ).count(),
        }

        metrics.update({
            'total_users': queryset.count(),
            'active_users': queryset.filter(is_active=True).count(),
            'department_breakdown': dept_counts,
            'role_breakdown': role_counts,
            'task_metrics': task_metrics,
        })

        return metrics

    def get_full_name(self, obj):
        """Display full name with optional job title."""
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        if not full_name:
            return obj.username

        if obj.job_title:
            return format_html(
                '{}<br><small style="color: #666;">{}</small>',
                full_name,
                obj.job_title
            )
        return full_name

    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'first_name'

    actions = ['mark_as_active', 'mark_as_inactive', 'mark_as_on_leave']

    def mark_as_active(self, request, queryset):
        """Bulk action to mark selected users as active."""
        queryset.update(status='active', is_active=True)

    mark_as_active.short_description = "Mark selected users as active"

    def mark_as_inactive(self, request, queryset):
        """Bulk action to mark selected users as inactive."""
        queryset.update(status='inactive', is_active=False)

    mark_as_inactive.short_description = "Mark selected users as inactive"

    def mark_as_on_leave(self, request, queryset):
        """Bulk action to mark selected users as on leave."""
        queryset.update(status='on_leave')

    mark_as_on_leave.short_description = "Mark selected users as on leave"

    def get_queryset(self, request):
        """Optimize queryset with select_related for related fields."""
        return super().get_queryset(request).select_related('reports_to')
