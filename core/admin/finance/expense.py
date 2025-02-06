from decimal import Decimal
from django.contrib import admin
from django.db.models import Sum, DecimalField
from rangefilter.filters import DateRangeFilter

from core.models import Expense
from core.admin.mixins import FinancialAdminMixin


@admin.register(Expense)
class ExpenseAdmin(FinancialAdminMixin, admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'display_amount',
        'vendor',
        'date',
        'status',
        'payment_method',
    )

    list_filter = (
        'status',
        'category',
        'payment_method',
        ('date', DateRangeFilter),
    )

    search_fields = (
        'title',
        'vendor',
        'description',
    )

    def get_summary_metrics(self, queryset):
        return {
            'total_expenses': queryset.aggregate(
                total=Sum('amount', output_field=DecimalField(max_digits=18, decimal_places=2))
            )['total'] or Decimal('0.00'),
            'category_totals': queryset.values('category') \
                .annotate(total=Sum('amount')) \
                .order_by('-total'),
            'monthly_totals': queryset.values('date__month', 'date__year') \
                .annotate(total=Sum('amount')) \
                .order_by('date__year', 'date__month'),
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
