from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from core.admin.mixins import MetricsMixin, StatusDisplayMixin, TimestampDisplayMixin
from core.models import Task


@admin.register(Task)
class TaskAdmin(
    StatusDisplayMixin, TimestampDisplayMixin, MetricsMixin, admin.ModelAdmin
):
    """
    Admin interface for Task model with enhanced display features using
    consolidated mixins for status, timestamps, and metrics.
    """

    list_display = (
        "name",
        "project",
        "display_assigned_to",
        "display_status",  # From StatusDisplayMixin
        "display_due_date",
        "display_priority",
        "display_created_at",  # From TimestampDisplayMixin
        "display_updated_at",  # From TimestampDisplayMixin
    )

    list_filter = (
        "status",
        "priority",
        "project",
        "assigned_to",
        ("due_date", DateRangeFilter),
        ("created_at", DateRangeFilter),
    )

    search_fields = (
        "name",
        "description",
        "project__name",
        "assigned_to__username",
        "assigned_to__first_name",
        "assigned_to__last_name",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "description",
                    ("status", "priority"),
                    "project",
                    "assigned_to",
                )
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    "due_date",
                    "estimated_hours",
                    "actual_hours",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def get_metrics(self, queryset):
        """
        Override get_metrics from MetricsMixin to include task-specific metrics.
        """
        metrics = super().get_metrics(queryset)

        status_counts = dict(
            queryset.values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )

        overdue_count = queryset.filter(
            Q(status__in=["planning", "in_progress"])
            & Q(due_date__lt=timezone.now().date())
        ).count()

        metrics.update(
            {
                "total_tasks": queryset.count(),
                "status_breakdown": status_counts,
                "overdue_tasks": overdue_count,
                "unassigned_tasks": queryset.filter(assigned_to__isnull=True).count(),
            }
        )
        return metrics

    def display_assigned_to(self, obj):
        """Display assigned user with link to their admin page."""
        if obj.assigned_to:
            return format_html(
                '<a href="/admin/core/user/{}/">{}</a>',
                obj.assigned_to.id,
                obj.assigned_to.get_full_name() or obj.assigned_to.username,
            )
        return format_html('<span style="color: #999;">Unassigned</span>')

    display_assigned_to.short_description = "Assigned To"

    def display_due_date(self, obj):
        """Display due date with color coding for overdue tasks."""
        if not obj.due_date:
            return "-"

        is_overdue = obj.due_date < timezone.now().date() and obj.status not in [
            "completed",
            "cancelled",
        ]

        formatted_date = self.format_date(obj.due_date)
        if is_overdue:
            return format_html('<span style="color: red;">{}</span>', formatted_date)
        return format_html("<span>{}</span>", formatted_date)

    display_due_date.short_description = "Due Date"

    def display_priority(self, obj):
        """Display priority with color coding."""
        priority_colors = {
            "high": "red",
            "medium": "orange",
            "low": "green",
        }
        color = priority_colors.get(obj.priority, "black")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_priority_display()
        )

    display_priority.short_description = "Priority"

    actions = ["mark_as_completed", "mark_as_in_progress"]

    def mark_as_completed(self, request, queryset):
        """Bulk action to mark selected tasks as completed."""
        queryset.update(status="completed", completion_date=timezone.now())

    mark_as_completed.short_description = "Mark selected tasks as completed"

    def mark_as_in_progress(self, request, queryset):
        """Bulk action to mark selected tasks as in progress."""
        queryset.update(status="in_progress")

    mark_as_in_progress.short_description = "Mark selected tasks as in progress"

    def get_queryset(self, request):
        """Optimize queryset with select_related for related fields."""
        return super().get_queryset(request).select_related("project", "assigned_to")
