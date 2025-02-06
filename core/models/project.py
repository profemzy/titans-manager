from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import Client
from core.models.mixins.timestamp import TimestampMixin


class Project(TimestampMixin):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In Progress"),
        ("on_hold", "On Hold"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    # Basic Information
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=20, unique=True, help_text="Unique project code/identifier"
    )
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planning")
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )

    # Relationships
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )
    manager = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="managed_projects"
    )
    team_members = models.ManyToManyField(
        "User", related_name="assigned_projects", blank=True
    )
    expenses = models.ManyToManyField("Expense", related_name="projects", blank=True)

    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)

    # Financial Information
    budget = models.DecimalField(
        max_digits=18, decimal_places=2, validators=[MinValueValidator(0)]
    )
    actual_cost = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    estimated_hours = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Additional Information
    github_repo = models.URLField(blank=True, null=True)
    documentation_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["client"]),
            models.Index(fields=["code"]),
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
        """Check if project is overdue."""
        if self.status != "completed" and self.end_date < timezone.now().date():
            return True
        return False

    @property
    def completion_percentage(self):
        """Calculate project completion percentage."""
        completed_tasks = self.tasks.filter(status="Completed").count()
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        return (completed_tasks / total_tasks) * 100

    @property
    def budget_utilized(self):
        """Calculate budget utilization percentage."""
        return (self.actual_cost / self.budget) * 100 if self.budget > 0 else 0

    @property
    def total_income(self):
        """Calculate total project income."""
        return self.incomes.aggregate(total=models.Sum("amount"))["total"] or 0

    @property
    def total_expenses(self):
        """Calculate total project expenses."""
        return self.expenses.aggregate(total=models.Sum("amount"))["total"] or 0

    @property
    def profit_margin(self):
        """Calculate project profit margin percentage."""
        if self.total_income == 0:
            return 0
        return (self.total_income - self.total_expenses) / self.total_income * 100

    def get_team_members_count(self):
        """Get total number of team members."""
        return self.team_members.count()

    def get_open_tasks_count(self):
        """Get count of open tasks."""
        return self.tasks.exclude(status="Completed").count()

    def get_project_duration(self):
        """Calculate project duration in days."""
        if self.actual_end_date and self.actual_start_date:
            return (self.actual_end_date - self.actual_start_date).days
        return (self.end_date - self.start_date).days
