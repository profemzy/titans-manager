from decimal import Decimal

from django.contrib import admin, messages
from django.db.models import DecimalField, Sum
from django.utils.html import format_html

from core.admin.mixins import FinancialAdminMixin
from core.models import Invoice
from core.services.finance import InvoiceService


@admin.register(Invoice)
class InvoiceAdmin(FinancialAdminMixin, admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "client",
        "project",
        "display_amount",
        "display_status",
        "date",
        "due_date",
    )

    list_filter = (
        "status",
        "date",
        "client",
        "project",
    )

    search_fields = (
        "invoice_number",
        "client__name",
        "project__name",
        "notes",
    )

    readonly_fields = ("invoice_number",)

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "invoice_number",
                    ("client", "project"),
                    ("date", "due_date"),
                    "amount",
                    "status",
                    "notes",
                )
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoice_service = InvoiceService()

    def display_status(self, obj):
        colors = {"draft": "grey", "sent": "blue", "paid": "green", "cancelled": "red"}
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    display_status.short_description = "Status"

    def get_summary_metrics(self, queryset):
        return {
            "total_invoices": queryset.aggregate(
                total=Sum(
                    "amount", output_field=DecimalField(max_digits=18, decimal_places=2)
                )
            )["total"]
            or Decimal("0.00"),
            "status_totals": queryset.values("status")
            .annotate(total=Sum("amount"))
            .order_by("-total"),
            "client_totals": queryset.values("client__name")
            .annotate(total=Sum("amount"))
            .order_by("-total"),
        }

    actions = ["mark_as_paid", "mark_as_sent"]

    def mark_as_paid(self, request, queryset):
        success_count = 0
        error_count = 0

        for invoice in queryset:
            try:
                # Use the service to mark as paid, which will create income record
                self.invoice_service.mark_as_paid(invoice, request.user)
                success_count += 1
            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f"Failed to mark invoice {invoice.invoice_number} as paid: {str(e)}",
                    messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"Successfully marked {success_count} invoice(s) as paid.",
                messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"Failed to mark {error_count} invoice(s) as paid. Check the error messages above.",
                messages.WARNING,
            )

    mark_as_paid.short_description = "Mark selected invoices as paid"

    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status="sent")
        self.message_user(
            request,
            f"Successfully marked {updated} invoice(s) as sent.",
            messages.SUCCESS,
        )

    mark_as_sent.short_description = "Mark selected invoices as sent"
