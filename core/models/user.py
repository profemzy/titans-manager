from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
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
