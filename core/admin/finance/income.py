from decimal import Decimal
from django.contrib import admin
from django.db.models import Sum, DecimalField
from rangefilter.filters import DateRangeFilter

from core.models import Income
from core.admin.mixins import FinancialAdminMixin


@admin.register(Income)
class IncomeAdmin(FinancialAdminMixin, admin.ModelAdmin):
    list_display = (
        'client',
        'project',
        'display_amount',
        'date',
        'invoice'
    )

    list_filter = (
        'client',
        'project',
        ('date', DateRangeFilter),
    )

    search_fields = (
        'client__name',
        'project__name',
    )

    def get_summary_metrics(self, queryset):
        return {
            'total_income': queryset.aggregate(
                total=Sum('amount', output_field=DecimalField(max_digits=18, decimal_places=2))
            )['total'] or Decimal('0.00'),
            'client_totals': queryset.values('client__name') \
                .annotate(total=Sum('amount')) \
                .order_by('-total'),
            'project_totals': queryset.values('project__name') \
                .annotate(total=Sum('amount')) \
                .order_by('-total')
        }

    def get_report_context(self, queryset, start_date, end_date):
        """Provide income-specific report context"""
        context = super().get_report_context(queryset, start_date, end_date)
        context.update({
            'client_totals': queryset.values('client__name')
            .annotate(total=Sum('amount'))
            .order_by('-total'),
            'project_totals': queryset.values('project__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        })
        return context
