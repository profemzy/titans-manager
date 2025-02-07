from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from core.admin.mixins import (
    FinancialMetricsMixin,
    StatusDisplayMixin,
    TimestampDisplayMixin,
)
from core.models import Client


@admin.register(Client)
class ClientAdmin(
    StatusDisplayMixin, FinancialMetricsMixin, TimestampDisplayMixin, admin.ModelAdmin
):
    """
    Admin interface for Client model with enhanced display features using
    consolidated mixins for status, financial metrics, and timestamps.
    """

    list_display = (
        "name",
        "company",
        "email",
        "display_status",  # From StatusDisplayMixin
        "display_projects",
        "display_revenue",  # From FinancialMetricsMixin
        "display_outstanding",  # From FinancialMetricsMixin
        "display_created_at",  # From TimestampDisplayMixin
    )

    list_filter = (
        "status",
        "industry",
        "country",
        ("created_at", DateRangeFilter),
    )

    search_fields = (
        "name",
        "email",
        "company",
        "phone",
        "address",
        "city",
        "tax_number",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "company",
                    "status",
                    "industry",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "email",
                    "alternate_email",
                    "phone",
                    "mobile_phone",
                    "website",
                )
            },
        ),
        (
            "Address Information",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            "Billing Information",
            {
                "fields": (
                    "billing_address",
                    "billing_email",
                    "payment_terms",
                    "tax_number",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
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
        Override get_metrics from FinancialMetricsMixin to include
        client-specific metrics.
        """
        metrics = super().get_metrics(queryset)
        metrics.update(
            {
                "active_clients": queryset.filter(status="active").count(),
                "total_projects": queryset.aggregate(total=Count("projects"))["total"]
                or 0,
            }
        )
        return metrics

    def display_projects(self, obj):
        """Display the number of projects as a clickable link."""
        return format_html(
            '<a href="/admin/core/project/?client__id__exact={}">{} projects</a>',
            obj.id,
            obj.projects.count(),
        )

    display_projects.short_description = "Projects"

    actions = ["mark_as_active", "mark_as_inactive"]

    def mark_as_active(self, request, queryset):
        """Bulk action to mark selected clients as active."""
        queryset.update(status="active")

    mark_as_active.short_description = "Mark selected clients as active"

    def mark_as_inactive(self, request, queryset):
        """Bulk action to mark selected clients as inactive."""
        queryset.update(status="inactive")

    mark_as_inactive.short_description = "Mark selected clients as inactive"
