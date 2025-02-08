from datetime import timedelta

import pytz
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from core.models import Task
from core.services.task_service import TaskService
from .factories import TaskFactory, ProjectFactory, UserFactory


class TaskServiceTest(TestCase):
    def setUp(self):
        self.service = TaskService()
        self.project = ProjectFactory()
        self.user = UserFactory()
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

    def test_create_task_success(self):
        """Test successful task creation with valid data"""
        task = self.service.create_task(
            name="Test Task",
            project_id=self.project.id,
            assigned_to_id=self.user.id,
            due_date=self.tomorrow,
            priority="medium",
        )

        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.project_id, self.project.id)
        self.assertEqual(task.assigned_to_id, self.user.id)
        self.assertEqual(task.due_date, self.tomorrow)
        self.assertEqual(task.priority, "medium")
        self.assertEqual(task.status, "pending")

    def test_create_task_past_due_date(self):
        """Test task creation with past due date raises error"""
        with self.assertRaises(ValidationError) as context:
            self.service.create_task(
                name="Test Task",
                project_id=self.project.id,
                assigned_to_id=self.user.id,
                due_date=self.yesterday,
            )
        self.assertIn("Due date cannot be in the past", str(context.exception))

    def test_create_task_with_optional_fields(self):
        """Test task creation with optional fields"""
        task = self.service.create_task(
            name="Test Task",
            project_id=self.project.id,
            assigned_to_id=self.user.id,
            due_date=self.tomorrow,
            description="Test Description",
            priority="high",
            estimated_hours=8,
        )

        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.estimated_hours, 8)

    @freeze_time("2025-02-07 12:00:00")
    def test_update_task_status_to_in_progress(self):
        """Test updating task status to in_progress sets started_at"""
        with timezone.override(pytz.UTC):
            task = TaskFactory(
                project=self.project, assigned_to=self.user, status="pending"
            )

            updated_task = self.service.update_task_status(
                task=task, new_status="in_progress", updated_by=self.user
            )

            self.assertEqual(updated_task.status, "in_progress")
            self.assertEqual(
                updated_task.started_at,
                timezone.datetime(2025, 2, 7, 12, 0).replace(tzinfo=pytz.UTC),
            )
            self.assertIsNone(updated_task.completed_at)

    @freeze_time("2025-02-07 12:00:00")
    def test_update_task_status_to_completed(self):
        """Test updating task status to completed sets completed_at"""
        with timezone.override(pytz.UTC):
            task = TaskFactory(
                project=self.project,
                assigned_to=self.user,
                status="in_progress",
                started_at=timezone.datetime(2025, 2, 6, 12, 0).replace(
                    tzinfo=pytz.UTC
                ),
            )

            updated_task = self.service.update_task_status(
                task=task, new_status="completed", updated_by=self.user
            )

            self.assertEqual(updated_task.status, "completed")
            self.assertEqual(
                updated_task.completed_at,
                timezone.datetime(2025, 2, 7, 12, 0).replace(tzinfo=pytz.UTC),
            )

    def test_update_task_same_status(self):
        """Test updating task with same status doesn't change timestamps"""
        initial_time = timezone.datetime(2025, 2, 1, 12, 0).replace(tzinfo=pytz.UTC)

        task = TaskFactory(
            project=self.project,
            assigned_to=self.user,
            status="in_progress",
            started_at=initial_time,
        )

        updated_task = self.service.update_task_status(
            task=task, new_status="in_progress", updated_by=self.user
        )

        self.assertEqual(updated_task.started_at, initial_time)

    def test_get_task_dependencies(self):
        """Test retrieving task dependencies"""
        # Create main task
        main_task = TaskFactory(
            project=self.project, assigned_to=self.user, status="in_progress"
        )

        # Create tasks that block main_task (dependencies)
        blocking_tasks = [
            TaskFactory(project=self.project, assigned_to=self.user, status="pending")
            for _ in range(2)
        ]

        # Add dependencies to main task
        main_task.dependencies.add(*blocking_tasks)

        # Create tasks that depend on main_task
        dependent_tasks = [
            TaskFactory(project=self.project, assigned_to=self.user, status="pending")
            for _ in range(2)
        ]

        # Set main_task as a dependency for these tasks
        for task in dependent_tasks:
            task.dependencies.add(main_task)

        # Get dependencies using the service
        dependencies = self.service.get_task_dependencies(main_task)

        # Verify blocking tasks (only pending/in_progress/blocked count as blocking)
        self.assertEqual(len(dependencies["blocking"]), 2)
        self.assertCountEqual(
            [t.id for t in dependencies["blocking"]], [t.id for t in blocking_tasks]
        )

        # Verify dependent tasks
        self.assertEqual(len(dependencies["dependent"]), 2)
        self.assertCountEqual(
            [t.id for t in dependencies["dependent"]], [t.id for t in dependent_tasks]
        )

    def test_get_blocking_tasks_status_filter(self):
        """Test that only pending/in_progress/blocked tasks are considered blocking"""
        main_task = TaskFactory(project=self.project, assigned_to=self.user)

        # Create tasks with different statuses
        pending_task = TaskFactory(status="pending")
        in_progress_task = TaskFactory(status="in_progress")
        blocked_task = TaskFactory(status="blocked")
        completed_task = TaskFactory(status="completed")
        cancelled_task = TaskFactory(status="cancelled")

        # Add all as dependencies
        main_task.dependencies.add(
            pending_task, in_progress_task, blocked_task, completed_task, cancelled_task
        )

        # Get dependencies
        dependencies = self.service.get_task_dependencies(main_task)
        blocking_task_ids = [t.id for t in dependencies["blocking"]]

        # Verify only appropriate tasks are considered blocking
        self.assertEqual(len(blocking_task_ids), 3)
        self.assertIn(pending_task.id, blocking_task_ids)
        self.assertIn(in_progress_task.id, blocking_task_ids)
        self.assertIn(blocked_task.id, blocking_task_ids)
        self.assertNotIn(completed_task.id, blocking_task_ids)
        self.assertNotIn(cancelled_task.id, blocking_task_ids)

    def test_can_start_task(self):
        """Test the can_start functionality"""
        task = TaskFactory(
            project=self.project, assigned_to=self.user, status="pending"
        )

        # Initially should be able to start
        self.assertTrue(task.can_start())

        # Add a blocking dependency
        blocking_task = TaskFactory(status="pending")
        task.dependencies.add(blocking_task)

        # Should not be able to start now
        self.assertFalse(task.can_start())

        # Complete the blocking task
        blocking_task.status = "completed"
        blocking_task.save()

        # Should be able to start again
        self.assertTrue(task.can_start())
