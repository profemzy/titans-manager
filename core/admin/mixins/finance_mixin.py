from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html

from core.services.finance.report_service import FinancialReportService


class FinancialAdminMixin:
    def display_amount(self, obj):
        formatted_amount = f"${float(obj.amount):,.2f}"
        return format_html("<span>{}</span>", formatted_amount)

    display_amount.short_description = "Amount"

    def get_summary_metrics(self, queryset):
        """
        Override this method in child classes to customize metrics calculation
        """
        raise NotImplementedError("Subclasses must implement get_summary_metrics()")

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        if not isinstance(response, TemplateResponse):
            return response

        queryset = response.context_data["cl"].queryset
        response.context_data["summary_metrics"] = self.get_summary_metrics(queryset)
        return response

    def get_urls(self):
        """Add report generation URL to all financial admin views"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate-report/",
                self.generate_report_view,
                name=f"{self.model._meta.model_name}-report",
            ),
        ]
        return custom_urls + urls

    def generate_report_view(self, request):
        """Shared report generation view"""
        from datetime import datetime

        report_service = FinancialReportService()

        # Get date range from request or filter
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        # If no dates provided, try to get from admin filter
        if not start_date and not end_date:
            date_filter = request.GET.get("date__range")
            if date_filter:
                start_date, end_date = date_filter.split(",")

        # Get filtered queryset
        queryset = self.get_queryset(request)

        # Filter by date if provided
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Generate PDF
        pdf_file = report_service.generate_financial_report(
            report_type=self.model._meta.model_name,
            start_date=start_date,
            end_date=end_date,
            queryset=queryset,
        )

        # Create filename with current date if no date range specified
        current_date = datetime.now().strftime("%Y-%m-%d")
        if start_date and end_date:
            filename = (
                f"{self.model._meta.model_name}_report_{start_date}_to_{end_date}.pdf"
            )
        else:
            filename = f"{self.model._meta.model_name}_report_{current_date}.pdf"

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def get_report_context(self, queryset, start_date, end_date):
        """
        Override this method in child classes to provide report-specific context
        """
        return {
            "queryset": queryset,
            "start_date": start_date,
            "end_date": end_date,
            "summary_metrics": self.get_summary_metrics(queryset),
        }
