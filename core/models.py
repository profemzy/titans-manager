import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Employee')

# Client Model
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

# Project Model
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    budget = models.DecimalField(max_digits=18, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name

# Task Model
class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    due_date = models.DateField()

    def __str__(self):
        return self.name

# Income Model
class Income(models.Model):
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='incomes')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='incomes')
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes')

    def __str__(self):
        return f"Income: {self.amount} on {self.date}"

# Expense Model
# models.py
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('rent', 'Rent/Lease'),
        ('utilities', 'Utilities'),
        ('software', 'Software/Tools'),
        ('hardware', 'Hardware/Equipment'),
        ('travel', 'Travel'),
        ('salaries', 'Salaries/Payroll'),
        ('marketing', 'Marketing'),
        ('office', 'Office Supplies'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes'),
        ('maintenance', 'Maintenance'),
        ('professional', 'Professional Services'),
        ('training', 'Training/Education'),
        ('other', 'Other')
    ]

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
    receipt = models.FileField(upload_to='receipts/%Y/%m/', null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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

# Invoice Model
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Unpaid')

    def __str__(self):
        return f"Invoice: {self.amount} for {self.client.name}"
