from datetime import date
from decimal import Decimal
from typing import Dict, List, Any
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from core.models import Project, User
from .base import BaseService


class ProjectService(BaseService[Project]):
    def __init__(self):
        super().__init__(Project)

    @transaction.atomic
    def create_project(self,
                       name: str,
                       client_id: int,
                       manager_id: int,
                       start_date: date,
                       end_date: date,
                       budget: Decimal,
                       code: str = None,
                       **kwargs) -> Project:
        """Create a new project with validation and business logic."""
        if end_date < start_date:
            raise ValidationError("End date cannot be before start date")

        if budget < 0:
            raise ValidationError("Budget cannot be negative")

        # Generate project code if not provided
        if not code:
            year = timezone.now().year
            count = Project.objects.filter(created_at__year=year).count()
            code = f"P{year}{str(count + 1).zfill(3)}"

        project = self.create(
            name=name,
            code=code,
            client_id=client_id,
            manager_id=manager_id,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            **kwargs
        )

        return project

    def assign_team_members(self, project: Project, member_ids: List[int]) -> Project:
        """Assign team members to a project."""
        users = User.objects.filter(id__in=member_ids)
        project.team_members.set(users)
        return project

    def get_project_metrics(self, project: Project) -> Dict[str, Any]:
        """Calculate project metrics."""
        return {
            'completion_percentage': project.completion_percentage,
            'budget_utilized': project.budget_utilized,
            'profit_margin': project.profit_margin,
            'total_tasks': project.tasks.count(),
            'completed_tasks': project.tasks.filter(status='completed').count(),
            'overdue_tasks': project.tasks.filter(
                status__in=['pending', 'in_progress'],
                due_date__lt=date.today()
            ).count()
        }

    def get_financial_summary(self, project: Project) -> Dict[str, Decimal]:
        """Get project financial summary."""
        return {
            'total_income': project.incomes.aggregate(
                total=Sum('amount'))['total'] or Decimal('0'),
            'total_expenses': project.expenses.aggregate(
                total=Sum('amount'))['total'] or Decimal('0'),
            'budget_remaining': project.budget - project.actual_cost
        }

    def search_projects(self, **filters) -> List[Project]:
        """Search projects with various filters."""
        queryset = self.model_class.objects.all()

        if 'status' in filters:
            queryset = queryset.filter(status=filters['status'])
        if 'client_id' in filters:
            queryset = queryset.filter(client_id=filters['client_id'])
        if 'manager_id' in filters:
            queryset = queryset.filter(manager_id=filters['manager_id'])
        if 'date_range' in filters:
            date_range = filters['date_range']
            queryset = queryset.filter(
                start_date__gte=date_range['start'],
                end_date__lte=date_range['end']
            )

        return list(queryset)
