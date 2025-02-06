from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from ..mixins.timestamp import TimestampMixin


class TaxCalculation(TimestampMixin):
    TAX_STATUS_CHOICES = [
        ('estimated', 'Estimated'),
        ('filed', 'Filed'),
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    ]

    QUARTER_CHOICES = [
        (1, 'Q1 (Jan-Mar)'),
        (2, 'Q2 (Apr-Jun)'),
        (3, 'Q3 (Jul-Sep)'),
        (4, 'Q4 (Oct-Dec)')
    ]

    # Basic Information
    tax_year = models.PositiveIntegerField(
        validators=[MinValueValidator(2000)],
        help_text="Tax year for this calculation"
    )
    quarter = models.PositiveIntegerField(
        choices=QUARTER_CHOICES,
        null=True,
        blank=True,
        help_text="Quarter for this calculation (if applicable)"
    )
    status = models.CharField(
        max_length=20,
        choices=TAX_STATUS_CHOICES,
        default='estimated',
        help_text="Current status of this tax calculation"
    )

    # Income and Expense Information
    total_income = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total income before deductions"
    )
    total_expenses = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total deductible expenses"
    )
    taxable_income = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Income subject to tax after deductions"
    )

    # Tax Calculations
    federal_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Federal portion of tax"
    )
    provincial_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Provincial portion of tax"
    )
    total_tax = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total tax payable (federal + provincial)"
    )

    # Payment Information
    installments_paid = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total tax installments already paid"
    )
    balance_due = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Remaining balance to be paid"
    )
    payment_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Due date for tax payment"
    )

    # Additional Information
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments about this tax calculation"
    )
    calculation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when this calculation was performed"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Date when this calculation was last updated"
    )

    class Meta:
        ordering = ['-tax_year', '-quarter']
        unique_together = ['tax_year', 'quarter']
        indexes = [
            models.Index(fields=['tax_year']),
            models.Index(fields=['calculation_date']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Tax Calculation'
        verbose_name_plural = 'Tax Calculations'

    def __str__(self):
        if self.quarter:
            return f"Tax Calculation - {self.tax_year} Q{self.quarter}"
        return f"Tax Calculation - {self.tax_year}"

    @property
    def effective_rate(self):
        """Calculate the effective tax rate"""
        if self.taxable_income == 0:
            return Decimal('0.00')
        return (self.total_tax / self.taxable_income * 100).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        # Calculate total tax
        self.total_tax = self.federal_tax + self.provincial_tax

        # Calculate balance due
        self.balance_due = self.total_tax - self.installments_paid

        # Calculate taxable income if not set
        if not self.taxable_income:
            self.taxable_income = max(Decimal('0.00'), self.total_income - self.total_expenses)

        super().save(*args, **kwargs)

    def is_paid(self):
        """Check if tax is fully paid"""
        return self.balance_due <= 0

    def get_payment_status(self):
        """Get detailed payment status"""
        if self.is_paid():
            return "Paid in full"
        elif self.installments_paid > 0:
            return f"Partially paid (${self.balance_due:,.2f} remaining)"
        return "No payments made"

    def is_overdue(self):
        """Check if payment is overdue"""
        if self.payment_due_date and self.balance_due > 0:
            from django.utils import timezone
            return timezone.now().date() > self.payment_due_date
        return False
