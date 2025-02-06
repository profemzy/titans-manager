from django.db import models
from django.utils import timezone
from . import Project, User
from django.core.validators import MinValueValidator

from .mixins.timestamp import TimestampMixin


class Task(TimestampMixin):
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
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES,
                                default='medium')
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                 default='feature')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                              default='pending')

    # Relations
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='tasks')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewing_tasks'
    )

    # Dates
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
        if (
            self.status != 'completed'
            and self.due_date < timezone.now().date()
        ):
            return True
        return False

    @property
    def time_spent(self):
        """Returns time spent in hours"""
        if self.started_at:
            end_time = (
                self.completed_at
                if self.completed_at
                else timezone.now()
            )
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
        """Calculate task completion percentage based on
        actual vs estimated hours"""
        if self.estimated_hours == 0:
            return 100 if self.status == 'completed' else 0
        return min(100, (self.actual_hours / self.estimated_hours) * 100)

    def get_blocking_tasks(self):
        """Returns tasks that are blocking this task"""
        return self.dependencies.filter(status__in=['pending', 'in_progress',
                                                    'blocked'])

    def can_start(self):
        """Check if task can be started (no blocking dependencies)"""
        return not self.get_blocking_tasks().exists()
