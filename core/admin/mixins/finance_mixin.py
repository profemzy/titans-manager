from django.template.response import TemplateResponse
from django.utils.html import format_html


class FinancialAdminMixin:
    def display_amount(self, obj):
        formatted_amount = f"${float(obj.amount):,.2f}"
        return format_html(
            '<span>{}</span>',
            formatted_amount
        )

    display_amount.short_description = 'Amount'

    def get_summary_metrics(self, queryset):
        """
        Override this method in child classes to customize metrics calculation
        """
        raise NotImplementedError("Subclasses must implement get_summary_metrics()")

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        if not isinstance(response, TemplateResponse):
            return response

        queryset = response.context_data['cl'].queryset
        response.context_data['summary_metrics'] = self.get_summary_metrics(queryset)
        return response
