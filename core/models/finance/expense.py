from django.db import models
import datetime
from . import CATEGORY_CHOICES
from ..mixins.timestamp import TimestampMixin
from ...custom_storage import AzureReceiptStorage


class Expense(TimestampMixin):

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('paypal', 'PayPal'),
        ('other', 'Other')
    ]

    TAX_STATUS_CHOICES = [
        ('taxable', 'Taxable'),
        ('non_taxable', 'Non-Taxable')
    ]

    RECURRING_CHOICES = [
        ('none', 'Not Recurring'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    # Categorization
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    tax_status = models.CharField(max_length=20, choices=TAX_STATUS_CHOICES, default='taxable')

    # Payment Details
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=100, blank=True, null=True,
                                         help_text="Reference number, cheque number, or transaction ID")

    # Dates
    date = models.DateField(help_text="Date of expense")
    due_date = models.DateField(null=True, blank=True, help_text="Due date for payment if applicable")
    paid_date = models.DateField(null=True, blank=True)

    # Recurring Information
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(max_length=20, choices=RECURRING_CHOICES, default='none')
    recurring_end_date = models.DateField(null=True, blank=True)

    # Documentation
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    vendor = models.CharField(max_length=200, blank=True, null=True)
    vendor_tax_number = models.CharField(max_length=50, blank=True, null=True)

    # Approval and Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses'
    )
    submitted_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='submitted_expenses'
    )

    # Metadata
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['is_recurring']),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.date})"

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"{self.category} Expense - {self.date}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return self.amount + self.tax_amount

    @property
    def is_overdue(self):
        if self.due_date and not self.paid_date:
            return self.due_date < datetime.date.today()
        return False

    def receipt_upload_path(instance, filename):
        """
        Generate the upload path for receipt files.
        Format: receipts/YYYY/MM/client_name/filename
        """
        from django.utils.text import slugify
        date = instance.date
        return f'receipts/{date.year}/{date.month:02d}/{slugify(instance.vendor or "unknown")}/{filename}'

    receipt = models.FileField(
        upload_to=receipt_upload_path,
        null=True,
        blank=True,
        storage=AzureReceiptStorage()
    )
