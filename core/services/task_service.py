from datetime import date, datetime
from typing import Dict, List

from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Task, User

from .base import BaseService


class TaskService(BaseService[Task]):
    def __init__(self):
        super().__init__(Task)

    @transaction.atomic
    def create_task(
        self, name: str, project_id: int, assigned_to_id: int, due_date: date, **kwargs
    ) -> Task:
        """Create a new task with validation."""
        if due_date < date.today():
            raise ValidationError("Due date cannot be in the past")

        task = self.create(
            name=name,
            project_id=project_id,
            assigned_to_id=assigned_to_id,
            due_date=due_date,
            **kwargs
        )

        return task

    @transaction.atomic
    def update_task_status(self, task: Task, new_status: str, updated_by: User) -> Task:
        """Update task status with proper tracking."""
        old_status = task.status

        if old_status == new_status:
            return task

        if new_status == "in_progress" and not task.started_at:
            task.started_at = datetime.now()
        elif new_status == "completed" and not task.completed_at:
            task.completed_at = datetime.now()

        task = self.update(task, status=new_status)

        # Could add status change logging here
        return task

    def get_task_dependencies(self, task: Task) -> Dict[str, List[Task]]:
        """Get task dependencies information."""
        return {
            "blocking": task.get_blocking_tasks(),
            "dependent": task.dependent_tasks.all(),
        }
