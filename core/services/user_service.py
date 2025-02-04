from datetime import datetime
from typing import Dict, Any

from core.models import User, Task
from .base import BaseService
from .. import models


class UserService(BaseService[User]):
    def __init__(self):
        super().__init__(User)

    def get_user_workload(self, user: User) -> Dict[str, Any]:
        """Get user's current workload metrics"""
        active_tasks = Task.objects.filter(
            assigned_to=user,
            status__in=['pending', 'in_progress']
        )

        return {
            'active_tasks_count': active_tasks.count(),
            'high_priority_tasks': active_tasks.filter(priority='high').count(),
            'overdue_tasks': active_tasks.filter(
                due_date__lt=datetime.now().date()
            ).count(),
            'projects_count': user.assigned_projects.count(),
            'total_estimated_hours': active_tasks.aggregate(
                total=models.Sum('estimated_hours')
            )['total'] or 0
        }

    def update_user_skills(self, user: User, skills: list) -> User:
        """Update user's skills"""
        user.skills = ','.join(skills)
        user.save()
        return user

    def get_team_members(self, user: User) -> list:
        """Get all team members reporting to user"""
        return self.model_class.objects.filter(reports_to=user)
