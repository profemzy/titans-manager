from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from core.admin.mixins import (
    FinancialMetricsMixin,
    StatusDisplayMixin,
    TimestampDisplayMixin,
)
from core.admin.task_inline import TaskInline
from core.models import Project


@admin.register(Project)
class ProjectAdmin(
    StatusDisplayMixin, FinancialMetricsMixin, TimestampDisplayMixin, admin.ModelAdmin
):
    """
    Admin interface for Project model with enhanced display features using
    consolidated mixins for status, financial metrics, and timestamps.
    """

    list_display = (
        "code",
        "name",
        "client",
        "display_status",  # From StatusDisplayMixin
        "manager",
        "display_timeline",
        "display_budget",
        "display_completion",
        "display_profit",  # Custom financial display
    )

    list_filter = (
        "status",
        "priority",
        "client",
        ("start_date", DateRangeFilter),
        ("end_date", DateRangeFilter),
    )

    search_fields = (
        "code",
        "name",
        "client__name",
        "description",
        "manager__username",
    )

    inlines = [TaskInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    ("code", "name"),
                    "description",
                    ("status", "priority"),
                    "client",
                    "manager",
                )
            },
        ),
        (
            "Timeline",
            {
                "fields": (
                    ("start_date", "end_date"),
                    ("actual_start_date", "actual_end_date"),
                )
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "budget",
                    "actual_cost",
                    ("hourly_rate", "estimated_hours"),
                )
            },
        ),
        (
            "Team",
            {
                "fields": ("team_members",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "github_repo",
                    "documentation_url",
                    "notes",
                ),
                "classes": ("collapse",),
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

    readonly_fields = ("code", "created_at", "updated_at")
    filter_horizontal = ("team_members",)

    def get_metrics(self, queryset):
        """
        Override get_metrics from FinancialMetricsMixin to include
        project-specific metrics.
        """
        metrics = super().get_metrics(queryset)

        total_budget = queryset.aggregate(total=Sum("budget"))["total"] or 0
        total_actual_cost = queryset.aggregate(total=Sum("actual_cost"))["total"] or 0
        total_profit = total_budget - total_actual_cost

        metrics.update(
            {
                "total_budget": total_budget,
                "total_actual_cost": total_actual_cost,
                "total_profit": total_profit,
                "active_projects": queryset.filter(
                    status__in=["planning", "in_progress"]
                ).count(),
            }
        )
        return metrics

    def display_profit(self, obj):
        """Display project profit/loss with color coding."""
        if not obj.budget or not obj.actual_cost:
            return self.format_currency(0)

        profit = obj.budget - obj.actual_cost
        color = "green" if profit >= 0 else "red"

        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.format_currency(abs(profit), ""),
        )

    display_profit.short_description = "Profit/Loss"

    def display_timeline(self, obj):
        """
        Display project timeline with color coding for overdue projects.
        Inherits date formatting from DisplayMixin.
        """
        is_overdue = obj.end_date < timezone.now().date() and obj.status not in [
            "completed",
            "cancelled",
        ]

        timeline = (
            f"{self.format_date(obj.start_date)} to {self.format_date(obj.end_date)}"
        )

        if is_overdue:
            return format_html('<span style="color: red;">{}</span>', timeline)
        return format_html("<span>{}</span>", timeline)

    display_timeline.short_description = "Timeline"

    def display_budget(self, obj):
        """Display project budget with consistent currency formatting."""
        budget = self.format_currency(obj.budget)
        actual = self.format_currency(obj.actual_cost)

        if obj.actual_cost and obj.actual_cost > obj.budget:
            return format_html(
                '<span>{} <span style="color: red;">({} actual)</span></span>',
                budget,
                actual,
            )
        return format_html("<span>{} ({} actual)</span>", budget, actual)

    display_budget.short_description = "Budget"

    def display_completion(self, obj):
        """Display project completion as a progress bar."""
        percentage = getattr(obj, "completion_percentage", 0)
        formatted_percentage = f"{float(percentage):.1f}%"

        return format_html(
            '<div class="progress-bar" style="width: 100px; background-color: #f1f1f1;">'
            '<div style="width: {}px; background-color: {}; height: 20px;"></div>'
            "</div> {}",
            min(percentage, 100),
            "#4CAF50" if percentage >= 100 else "#2196F3",
            formatted_percentage,
        )

    display_completion.short_description = "Completion"

    actions = ["mark_as_completed", "mark_as_on_hold"]

    def mark_as_completed(self, request, queryset):
        """Bulk action to mark selected projects as completed."""
        queryset.update(status="completed", actual_end_date=timezone.now().date())

    mark_as_completed.short_description = "Mark selected projects as completed"

    def mark_as_on_hold(self, request, queryset):
        """Bulk action to mark selected projects as on hold."""
        queryset.update(status="on_hold")

    mark_as_on_hold.short_description = "Mark selected projects as on hold"

    class Media:
        css = {"all": ["admin/css/progress-bar.css"]}
