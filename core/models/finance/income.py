import datetime

from django.db import models

from .. import Project
from ..mixins.timestamp import TimestampMixin
from ..client import Client


class Income(TimestampMixin):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("cheque", "Cheque"),
        ("bank_transfer", "Bank Transfer"),
        ("credit_card", "Credit Card"),
        ("paypal", "PayPal"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("received", "Received"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    INCOME_TYPE_CHOICES = [
        ("project_payment", "Project Payment"),
        ("retainer", "Retainer Fee"),
        ("consultation", "Consultation"),
        ("maintenance", "Maintenance"),
        ("other", "Other"),
    ]

    # Basic Information
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)

    # Relations
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="incomes")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="incomes"
    )
    invoice = models.ForeignKey(
        "Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incomes",
    )

    # Payment Details
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default="bank_transfer"
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction ID, cheque number, etc.",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    income_type = models.CharField(max_length=50, choices=INCOME_TYPE_CHOICES)

    # Additional Information
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # Tax Information
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["income_type"]),
        ]
        verbose_name = "Income"
        verbose_name_plural = "Income"

    def __str__(self):
        return f"Income: ${self.amount} from {self.client.name} ({self.date})"

    def save(self, *args, **kwargs):
        # Calculate tax amount before saving
        if self.tax_rate > 0:
            self.tax_amount = self.amount * (self.tax_rate / 100)
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        """Total amount including tax"""
        return self.amount + self.tax_amount

    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.expected_date and self.status == "pending":
            return self.expected_date < datetime.date.today()
        return False

    @property
    def days_overdue(self):
        """Calculate number of days payment is overdue"""
        if self.is_overdue:
            return (datetime.date.today() - self.expected_date).days
        return 0
