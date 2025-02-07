from django.db.models import Q, Sum
from django.template.response import TemplateResponse
from django.utils.html import format_html


class DisplayMixin:
    """Base mixin for common display formatting functionality."""

    def format_currency(self, amount, default="$0.00"):
        """Format amount as currency."""
        if amount:
            return f"${float(amount):,.2f}"
        return default

    def format_date(self, date, format_string="%Y-%m-%d"):
        """Format date with consistent styling."""
        if date:
            return date.strftime(format_string)
        return "-"


class StatusDisplayMixin(DisplayMixin):
    """Mixin for displaying status with color coding."""

    status_colors = {
        # Project/Task statuses
        "planning": "blue",
        "in_progress": "orange",
        "on_hold": "red",
        "completed": "green",
        "cancelled": "grey",
        # User/Client statuses
        "active": "green",
        "inactive": "red",
        "prospect": "blue",
        "former": "grey",
    }

    def display_status(self, obj):
        """Display status with appropriate color coding."""
        color = self.status_colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_status_display()
        )

    display_status.short_description = "Status"


class MetricsMixin:
    """Mixin for aggregate metrics and summary statistics."""

    def get_metrics(self, queryset):
        """Override this method to define custom metrics for different models."""
        return {
            "total_items": queryset.count(),
        }

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        if not isinstance(response, TemplateResponse):
            return response

        queryset = response.context_data["cl"].queryset
        response.context_data["summary_metrics"] = self.get_metrics(queryset)
        return response


class TimestampDisplayMixin(DisplayMixin):
    """Mixin for displaying creation and update timestamps."""

    def display_created_at(self, obj):
        return format_html(
            "<span>{}</span>", self.format_date(obj.created_at, "%Y-%m-%d %H:%M:%S")
        )

    display_created_at.short_description = "Created At"

    def display_updated_at(self, obj):
        return format_html(
            "<span>{}</span>", self.format_date(obj.updated_at, "%Y-%m-%d %H:%M:%S")
        )

    display_updated_at.short_description = "Updated At"


class WorkloadDisplayMixin:
    """Mixin for displaying user workload information."""

    def display_workload(self, obj):
        active_tasks = obj.tasks.exclude(status="completed").count()
        total_tasks = obj.tasks.count()
        if total_tasks:
            return format_html("{} active / {} total", active_tasks, total_tasks)
        return "0 tasks"

    display_workload.short_description = "Workload"


class ReportsToDisplayMixin:
    """Mixin for displaying reporting relationships."""

    def display_reports_to(self, obj):
        if obj.reports_to:
            return format_html(
                '<a href="{}/">{}</a>',
                obj.reports_to.id,
                obj.reports_to.get_full_name() or obj.reports_to.username,
            )
        return "-"

    display_reports_to.short_description = "Reports To"


class FinancialMetricsMixin(MetricsMixin):
    """Mixin specifically for financial metrics."""

    def get_metrics(self, queryset):
        metrics = super().get_metrics(queryset)
        metrics.update(
            {
                "total_revenue": queryset.aggregate(total=Sum("incomes__amount"))[
                    "total"
                ]
                or 0,
                "total_outstanding": queryset.aggregate(
                    total=Sum("invoices__amount", filter=Q(invoices__status="Unpaid"))
                )["total"]
                or 0,
            }
        )
        return metrics

    def display_revenue(self, obj):
        return self.format_currency(obj.total_revenue)

    display_revenue.short_description = "Total Revenue"

    def display_outstanding(self, obj):
        if obj.total_outstanding > 0:
            return format_html(
                '<span style="color: red;">{}</span>',
                self.format_currency(obj.total_outstanding),
            )
        return self.format_currency(0)

    display_outstanding.short_description = "Outstanding"
