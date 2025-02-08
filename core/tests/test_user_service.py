from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from freezegun import freeze_time

from core.models import User
from core.services.user_service import UserService
from .factories import ProjectFactory, TaskFactory, UserFactory


class UserServiceTest(TestCase):
    def setUp(self):
        self.service = UserService()
        self.user = UserFactory(
            username="testuser",
            email="test@example.com",
            role="Employee",
            department="development",
        )
        self.manager = UserFactory(role="Manager")
        self.project = ProjectFactory(manager=self.manager)

    def test_get_user_workload(self):
        # Create some tasks for the user
        TaskFactory(
            project=self.project,
            assigned_to=self.user,
            status="pending",
            priority="high",
            estimated_hours=Decimal("4.00"),
        )
        TaskFactory(
            project=self.project,
            assigned_to=self.user,
            status="in_progress",
            priority="medium",
            estimated_hours=Decimal("6.00"),
        )
        # Create an overdue task
        yesterday = date.today() - timedelta(days=1)
        TaskFactory(
            project=self.project,
            assigned_to=self.user,
            status="pending",
            due_date=yesterday,
            estimated_hours=Decimal("2.00"),
        )

        workload = self.service.get_user_workload(self.user)

        self.assertEqual(workload["active_tasks_count"], 3)
        self.assertEqual(workload["high_priority_tasks"], 1)
        self.assertEqual(workload["overdue_tasks"], 1)
        self.assertEqual(workload["total_estimated_hours"], Decimal("12.00"))

    def test_update_user_skills(self):
        skills = ["Python", "Django", "JavaScript"]
        updated_user = self.service.update_user_skills(self.user, skills)

        self.assertEqual(updated_user.skills, "Python,Django,JavaScript")

        # Verify skills persisted to database
        user_from_db = User.objects.get(id=self.user.id)
        self.assertEqual(user_from_db.skills, "Python,Django,JavaScript")

    def test_get_team_members(self):
        # Create team members reporting to the manager
        team_member1 = UserFactory(reports_to=self.manager)
        team_member2 = UserFactory(reports_to=self.manager)
        # Create another user not reporting to the manager
        UserFactory()

        team_members = self.service.get_team_members(self.manager)

        self.assertEqual(len(team_members), 2)
        self.assertIn(team_member1, team_members)
        self.assertIn(team_member2, team_members)

    @freeze_time("2025-02-07")
    def test_user_workload_with_completed_tasks(self):
        # Create both active and completed tasks
        TaskFactory(
            project=self.project,
            assigned_to=self.user,
            status="completed",
            priority="high",
            estimated_hours=Decimal("4.00"),
        )
        TaskFactory(
            project=self.project,
            assigned_to=self.user,
            status="pending",
            priority="high",
            estimated_hours=Decimal("6.00"),
        )

        workload = self.service.get_user_workload(self.user)

        # Should only count active tasks
        self.assertEqual(workload["active_tasks_count"], 1)
        self.assertEqual(workload["high_priority_tasks"], 1)
        self.assertEqual(workload["total_estimated_hours"], Decimal("6.00"))

    def test_update_user_skills_empty_list(self):
        # Test updating with empty skills list
        updated_user = self.service.update_user_skills(self.user, [])
        self.assertEqual(updated_user.skills, "")

    def test_get_team_members_no_reports(self):
        # Test getting team members for user with no direct reports
        regular_user = UserFactory(role="Employee")
        team_members = self.service.get_team_members(regular_user)
        self.assertEqual(len(team_members), 0)
