import django_filters
from . import models

class ProjectFilter(django_filters.FilterSet):
    start_date_after = django_filters.DateFilter(
        field_name='start_date', lookup_expr='gte'
    )
    start_date_before = django_filters.DateFilter(
        field_name='start_date', lookup_expr='lte'
    )
    budget_min = django_filters.NumberFilter(
        field_name='budget', lookup_expr='gte'
    )
    budget_max = django_filters.NumberFilter(
        field_name='budget', lookup_expr='lte'
    )

    class Meta:
        model = models.Project
        fields = {
            'status': ['exact'],
            'priority': ['exact'],
            'client': ['exact'],
            'manager': ['exact'],
        }


class TaskFilter(django_filters.FilterSet):
    due_date_after = django_filters.DateFilter(
        field_name='due_date', lookup_expr='gte'
    )
    due_date_before = django_filters.DateFilter(
        field_name='due_date', lookup_expr='lte'
    )
    estimated_hours_min = django_filters.NumberFilter(
        field_name='estimated_hours', lookup_expr='gte'
    )
    estimated_hours_max = django_filters.NumberFilter(
        field_name='estimated_hours', lookup_expr='lte'
    )

    class Meta:
        model = models.Task
        fields = {
            'status': ['exact'],
            'priority': ['exact'],
            'project': ['exact'],
            'assigned_to': ['exact'],
            'reviewer': ['exact'],
            'task_type': ['exact'],
        }


class ExpenseFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(
        field_name='date', lookup_expr='gte'
    )
    date_before = django_filters.DateFilter(
        field_name='date', lookup_expr='lte'
    )
    amount_min = django_filters.NumberFilter(
        field_name='amount', lookup_expr='gte'
    )
    amount_max = django_filters.NumberFilter(
        field_name='amount', lookup_expr='lte'
    )

    class Meta:
        model = models.Expense
        fields = {
            'category': ['exact'],
            'payment_method': ['exact'],
            'tax_status': ['exact'],
            'status': ['exact'],
            'is_recurring': ['exact'],
            'submitted_by': ['exact'],
            'approved_by': ['exact'],
        }
