import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
        ('Contractor', 'Contractor'),
        ('Intern', 'Intern')
    ]

    DEPARTMENT_CHOICES = [
        ('management', 'Management'),
        ('development', 'Development'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('hr', 'Human Resources'),
        ('finance', 'Finance'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive')
    ]

    # Role and Department
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Employee')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)

    # Work Information
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    hire_date = models.DateField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Skills and Expertise
    skills = models.CharField(max_length=500, blank=True, null=True,
                              help_text="Comma-separated list of skills")
    certifications = models.TextField(blank=True, null=True)

    # Work Schedule
    working_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=40.00,
        help_text="Weekly working hours"
    )
    time_zone = models.CharField(max_length=50, default='UTC',
                                 help_text="User's primary timezone")

    # System Access
    last_password_change = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    last_login_attempt = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['username']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['department']),
            models.Index(fields=['status']),
            models.Index(fields=['employee_id']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def save(self, *args, **kwargs):
        if not self.employee_id and self.role != 'Admin':
            # Generate employee ID if not provided
            year = str(timezone.now().year)[2:]
            dept = self.department[:2].upper() if self.department else 'EM'
            count = User.objects.filter(
                employee_id__startswith=f"{year}{dept}"
            ).count()
            self.employee_id = f"{year}{dept}{str(count + 1).zfill(3)}"
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def is_manager(self):
        return self.role in ['Admin', 'Manager']

    @property
    def direct_reports_count(self):
        return self.subordinates.count()

    def get_current_tasks(self):
        return self.tasks.exclude(status='Completed')

    def get_completed_tasks(self):
        return self.tasks.filter(status='Completed')

    def get_assigned_projects(self):
        return self.assigned_projects.all()

    def get_managed_projects(self):
        return self.managed_projects.all()

    def get_total_hours_worked(self, start_date=None, end_date=None):
        tasks = self.tasks.filter(status='Completed')
        if start_date:
            tasks = tasks.filter(completed_at__gte=start_date)
        if end_date:
            tasks = tasks.filter(completed_at__lte=end_date)
        return sum(task.actual_hours for task in tasks)


class Client(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('prospect', 'Prospect'),
        ('former', 'Former')
    ]

    # Basic Information
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)

    # Contact Information
    alternate_email = models.EmailField(blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Address Information
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Business Information
    tax_number = models.CharField(max_length=50, blank=True, null=True, help_text="VAT/GST/Tax ID")
    industry = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)

    # Billing Information
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    billing_email = models.EmailField(blank=True, null=True)
    payment_terms = models.IntegerField(default=30, help_text="Payment terms in days")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at'])
        ]

    def __str__(self):
        if self.company:
            return f"{self.name} ({self.company})"
        return self.name

    def get_full_address(self):
        """Returns formatted full address"""
        parts = [
            self.address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, parts))

    @property
    def total_projects(self):
        """Returns total number of projects"""
        return self.projects.count()

    @property
    def total_revenue(self):
        """Returns total revenue from client"""
        return self.incomes.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def outstanding_invoices(self):
        """Returns queryset of unpaid invoices"""
        return self.invoices.filter(status='Unpaid')

    @property
    def total_outstanding(self):
        """Returns total amount of unpaid invoices"""
        return self.outstanding_invoices.aggregate(
            total=models.Sum('amount'))['total'] or 0

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]

    # Basic Information
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, help_text="Unique project code/identifier")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    # Relationships
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    manager = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    team_members = models.ManyToManyField('User', related_name='assigned_projects', blank=True)

    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)

    # Financial Information
    budget = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0)])
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Additional Information
    github_repo = models.URLField(blank=True, null=True)
    documentation_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['client']),
            models.Index(fields=['code'])
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate project code if not provided
            year = timezone.now().year
            count = Project.objects.filter(created_at__year=year).count()
            self.code = f"P{year}{str(count + 1).zfill(3)}"
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status != 'completed' and self.end_date < timezone.now().date():
            return True
        return False

    @property
    def completion_percentage(self):
        completed_tasks = self.tasks.filter(status='Completed').count()
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        return (completed_tasks / total_tasks) * 100

    @property
    def budget_utilized(self):
        return (self.actual_cost / self.budget) * 100 if self.budget > 0 else 0

    @property
    def total_income(self):
        return self.incomes.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def total_expenses(self):
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def profit_margin(self):
        if self.total_income == 0:
            return 0
        return ((self.total_income - self.total_expenses) / self.total_income) * 100

    def get_team_members_count(self):
        return self.team_members.count()

    def get_open_tasks_count(self):
        return self.tasks.exclude(status='Completed').count()

    def get_project_duration(self):
        if self.actual_end_date and self.actual_start_date:
            return (self.actual_end_date - self.actual_start_date).days
        return (self.end_date - self.start_date).days


from django.core.validators import MinValueValidator
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]

    TYPE_CHOICES = [
        ('feature', 'Feature'),
        ('bug', 'Bug'),
        ('improvement', 'Improvement'),
        ('maintenance', 'Maintenance'),
        ('documentation', 'Documentation'),
        ('other', 'Other')
    ]

    # Basic Information
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='feature')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    # Relations
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewing_tasks'
    )

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Time Tracking
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    # Dependencies
    dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='dependent_tasks',
        blank=True
    )

    # Additional Information
    github_issue = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True,
                            help_text="Comma-separated tags")

    class Meta:
        ordering = ['-priority', 'due_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.name} ({self.project.name})"

    def save(self, *args, **kwargs):
        if self.status == 'in_progress' and not self.started_at:
            self.started_at = timezone.now()
        elif self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status != 'completed' and self.due_date < timezone.now().date():
            return True
        return False

    @property
    def time_spent(self):
        """Returns time spent in hours"""
        if self.started_at:
            end_time = self.completed_at if self.completed_at else timezone.now()
            duration = end_time - self.started_at
            return round(duration.total_seconds() / 3600, 2)
        return 0

    @property
    def time_remaining(self):
        """Returns estimated time remaining in hours"""
        if self.status == 'completed':
            return 0
        return max(0, self.estimated_hours - self.actual_hours)

    @property
    def completion_percentage(self):
        """Calculate task completion percentage based on actual vs estimated hours"""
        if self.estimated_hours == 0:
            return 100 if self.status == 'completed' else 0
        return min(100, (self.actual_hours / self.estimated_hours) * 100)

    def get_blocking_tasks(self):
        """Returns tasks that are blocking this task"""
        return self.dependencies.filter(status__in=['pending', 'in_progress', 'blocked'])

    def can_start(self):
        """Check if task can be started (no blocking dependencies)"""
        return not self.get_blocking_tasks().exists()


class Income(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    INCOME_TYPE_CHOICES = [
        ('project_payment', 'Project Payment'),
        ('retainer', 'Retainer Fee'),
        ('consultation', 'Consultation'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other')
    ]

    # Basic Information
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)

    # Relations
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='incomes')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='incomes')
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes')

    # Payment Details
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    payment_reference = models.CharField(max_length=100, blank=True, null=True,
                                         help_text="Transaction ID, cheque number, etc.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    income_type = models.CharField(max_length=50, choices=INCOME_TYPE_CHOICES)

    # Additional Information
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # Tax Information
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['income_type']),
        ]
        verbose_name = 'Income'
        verbose_name_plural = 'Income'

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
        if self.expected_date and self.status == 'pending':
            return self.expected_date < datetime.date.today()
        return False

    @property
    def days_overdue(self):
        """Calculate number of days payment is overdue"""
        if self.is_overdue:
            return (datetime.date.today() - self.expected_date).days
        return 0

# Expense Model
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


from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('paypal', 'PayPal'),
        ('other', 'Other')
    ]

    # Basic Information
    invoice_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')

    # Dates
    date = models.DateField(help_text="Invoice issue date")
    due_date = models.DateField(help_text="Payment due date")
    paid_date = models.DateField(null=True, blank=True)

    # Financial Details
    amount = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    # Status and Payment
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Reference number for the payment"
    )

    # Additional Information
    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    private_notes = models.TextField(blank=True, null=True, help_text="Internal notes")

    # File Attachments
    pdf_file = models.FileField(upload_to='invoices/pdf/%Y/%m/', null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices'
    )

    class Meta:
        ordering = ['-date', '-invoice_number']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['client']),
        ]

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.client.name} (${self.amount:,.2f})"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number: INV-YYYYMM-XXXX
            year_month = timezone.now().strftime('%Y%m')
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f'INV-{year_month}'
            ).order_by('invoice_number').last()

            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.invoice_number = f'INV-{year_month}-{str(new_number).zfill(4)}'

        # Calculate tax amount
        if self.tax_rate > 0:
            self.tax_amount = (self.amount * self.tax_rate) / 100

        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        """Calculate total amount including tax and discount"""
        return self.amount + self.tax_amount - self.discount

    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.total_amount - self.paid_amount

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status not in ['paid', 'cancelled', 'refunded']:
            return self.due_date < timezone.now().date()
        return False

    @property
    def days_overdue(self):
        """Calculate number of days overdue"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

    def mark_as_paid(self, payment_method=None, payment_reference=None, paid_date=None):
        """Mark invoice as paid"""
        self.status = 'paid'
        self.payment_method = payment_method
        self.payment_reference = payment_reference
        self.paid_date = paid_date or timezone.now().date()
        self.paid_amount = self.total_amount
        self.save()

    def record_partial_payment(self, amount, payment_method=None, payment_reference=None):
        """Record a partial payment"""
        self.paid_amount += amount
        self.payment_method = payment_method
        self.payment_reference = payment_reference

        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        else:
            self.status = 'partially_paid'

        self.save()
