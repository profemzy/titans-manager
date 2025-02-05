from decimal import Decimal
from django.contrib import admin
from django.db.models import Sum, DecimalField
from django.utils.html import format_html

from core.models import Invoice
from core.admin.mixins import FinancialAdminMixin


@admin.register(Invoice)
class InvoiceAdmin(FinancialAdminMixin, admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'client',
        'project',
        'display_amount',
        'display_status',
        'date',
        'due_date'
    )

    list_filter = (
        'status',
        'date',
        'client',
        'project',
    )

    search_fields = (
        'invoice_number',
        'client__name',
        'project__name',
        'notes',
    )

    readonly_fields = ('invoice_number',)

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'invoice_number',
                ('client', 'project'),
                ('date', 'due_date'),
                'amount',
                'status',
                'notes',
            )
        }),
    )

    def display_status(self, obj):
        colors = {
            'draft': 'grey',
            'sent': 'blue',
            'paid': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    display_status.short_description = 'Status'

    def get_summary_metrics(self, queryset):
        return {
            'total_invoices': queryset.aggregate(
                total=Sum('amount', output_field=DecimalField(max_digits=18, decimal_places=2))
            )['total'] or Decimal('0.00'),
            'status_totals': queryset.values('status') \
                .annotate(total=Sum('amount')) \
                .order_by('-total'),
            'client_totals': queryset.values('client__name') \
                .annotate(total=Sum('amount')) \
                .order_by('-total'),
        }

    actions = ['mark_as_paid', 'mark_as_sent']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')

    mark_as_paid.short_description = "Mark selected invoices as paid"

    def mark_as_sent(self, request, queryset):
        queryset.update(status='sent')

    mark_as_sent.short_description = "Mark selected invoices as sent"
