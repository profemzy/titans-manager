from decimal import Decimal

from django.contrib import admin
from django.db.models import Sum, DecimalField, Count
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter

from core.admin.mixins import FinancialAdminMixin
from core.models import TaxCalculation
from core.services.finance.expense_service import ExpenseService
from core.services.finance.income_service import IncomeService
from core.services.finance.tax_service import TaxCalculationService


@admin.register(TaxCalculation)
class TaxAdmin(FinancialAdminMixin, admin.ModelAdmin):
    change_list_template = 'admin/tax_calculation_change_list.html'

    list_display = (
        'tax_year',
        'display_total_tax',
        'display_federal_amount',
        'display_provincial_amount',
        'display_effective_rate',
    )

    list_filter = (
        ('tax_year', DateRangeFilter),
        'quarter',
    )

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.income_service = IncomeService()
        self.expense_service = ExpenseService()
        self.tax_service = TaxCalculationService(
            income_service=self.income_service,
            expense_service=self.expense_service
        )

    def display_total_tax(self, obj):
        formatted_amount = f"${float(obj.total_tax):,.2f}"
        return format_html(
            '<span>{}</span>',
            formatted_amount
        )

    display_total_tax.short_description = 'Total Tax'

    def display_federal_amount(self, obj):
        formatted_amount = f"${float(obj.federal_tax):,.2f}"
        return format_html(
            '<span>{}</span>',
            formatted_amount
        )

    display_federal_amount.short_description = 'Federal Tax'

    def display_provincial_amount(self, obj):
        formatted_amount = f"${float(obj.provincial_tax):,.2f}"
        return format_html(
            '<span>{}</span>',
            formatted_amount
        )

    display_provincial_amount.short_description = 'Provincial Tax'

    def display_effective_rate(self, obj):
        if obj.taxable_income:
            rate = (obj.total_tax / obj.taxable_income * 100)
            return format_html(
                '<span>{}%</span>',
                float(rate)
            )
        return format_html('<span>0.00%</span>')

    display_effective_rate.short_description = 'Effective Rate'

    def display_amount(self, obj):
        return self.display_total_tax(obj)

    def get_summary_metrics(self, queryset):
        """
        Implements the required get_summary_metrics method from FinancialAdminMixin
        """
        summary = {
            'total_tax_payable': queryset.aggregate(
                total=Sum('total_tax', output_field=DecimalField(max_digits=18, decimal_places=2))
            )['total'] or Decimal('0.00'),

            'federal_total': queryset.aggregate(
                total=Sum('federal_tax', output_field=DecimalField(max_digits=18, decimal_places=2))
            )['total'] or Decimal('0.00'),

            'provincial_total': queryset.aggregate(
                total=Sum('provincial_tax', output_field=DecimalField(max_digits=18, decimal_places=2))
            )['total'] or Decimal('0.00'),

            'yearly_summary': queryset.values('tax_year').annotate(
                total_tax=Sum('total_tax'),
                federal_tax=Sum('federal_tax'),
                provincial_tax=Sum('provincial_tax'),
            ).order_by('-tax_year'),

            'quarterly_summary': queryset.values('tax_year', 'quarter').annotate(
                total_tax=Sum('total_tax'),
                federal_tax=Sum('federal_tax'),
                provincial_tax=Sum('provincial_tax')
            ).order_by('-tax_year', 'quarter')
        }

        # Calculate effective rates for yearly summary
        for year in summary['yearly_summary']:
            year_queryset = queryset.filter(tax_year=year['tax_year'])
            total_taxable_income = year_queryset.aggregate(
                total=Sum('taxable_income'))['total'] or Decimal('0.00')
            if total_taxable_income > 0:
                year['effective_rate'] = (year['total_tax'] / total_taxable_income * 100)
            else:
                year['effective_rate'] = Decimal('0.00')

        return summary
