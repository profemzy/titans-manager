from decimal import Decimal
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db import models

from core.models.mixins.timestamp import TimestampMixin


class Invoice(TimestampMixin):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    # Basic Information
    invoice_number = models.CharField(
        max_length=50, unique=True, editable=False
    )  # Changed to editable=False
    client = models.ForeignKey(
        "Client", on_delete=models.CASCADE, related_name="invoices"
    )
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="invoices"
    )

    # Dates and Amount
    date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # Notes
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.client.name}"

    def generate_invoice_number(self):
        """Generate a unique invoice number"""
        year_month = timezone.now().strftime("%Y%m")
        last_invoice = (
            Invoice.objects.filter(invoice_number__startswith=f"INV-{year_month}")
            .order_by("invoice_number")
            .last()
        )

        if last_invoice:
            last_number = int(last_invoice.invoice_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"INV-{year_month}-{str(new_number).zfill(4)}"

    def save(self, *args, **kwargs):
        # Only generate number if this is a new invoice
        if not self.pk and not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()

        super().save(*args, **kwargs)
