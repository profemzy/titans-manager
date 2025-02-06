from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from decimal import Decimal

from core.services.project_service import ProjectService
from core.models import Project
from .factories import UserFactory, ClientFactory, ProjectFactory


class ProjectServiceTest(TestCase):
    def setUp(self):
        self.service = ProjectService()
        self.client = ClientFactory()
        self.manager = UserFactory()
        self.start_date = date.today()
        self.end_date = self.start_date + timedelta(days=30)

    def test_create_project_success(self):
        project = self.service.create_project(
            name="Test Project",
            client_id=self.client.id,
            manager_id=self.manager.id,
            start_date=self.start_date,
            end_date=self.end_date,
            budget=Decimal("1000.00"),
        )

        self.assertIsInstance(project, Project)
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.client_id, self.client.id)
        self.assertEqual(project.manager_id, self.manager.id)
        self.assertIsNotNone(project.code)  # Verify code was generated
        self.assertTrue(project.code.startswith("P"))

    def test_create_project_invalid_dates(self):
        with self.assertRaises(ValidationError):
            self.service.create_project(
                name="Test Project",
                client_id=self.client.id,
                manager_id=self.manager.id,
                start_date=self.end_date,  # End date before start date
                end_date=self.start_date,
                budget=Decimal("1000.00"),
            )

    def test_create_project_negative_budget(self):
        with self.assertRaises(ValidationError):
            self.service.create_project(
                name="Test Project",
                client_id=self.client.id,
                manager_id=self.manager.id,
                start_date=self.start_date,
                end_date=self.end_date,
                budget=Decimal("-1000.00"),
            )

    def test_assign_team_members(self):
        project = ProjectFactory(
            client=self.client,
            manager=self.manager,
            start_date=self.start_date,
            end_date=self.end_date,
            budget=Decimal("1000.00"),
        )

        team_members = [UserFactory() for _ in range(3)]
        member_ids = [user.id for user in team_members]

        # Using the instance method via self.service
        updated_project = self.service.assign_team_members(project, member_ids)
        self.assertEqual(updated_project.team_members.count(), 3)
        self.assertEqual(
            set(updated_project.team_members.values_list("id", flat=True)),
            set(member_ids),
        )

    def test_get_project_metrics(self):
        project = ProjectFactory(
            client=self.client,
            manager=self.manager,
            start_date=self.start_date,
            end_date=self.end_date,
            budget=Decimal("1000.00"),
        )

        # Using the instance method
        metrics = self.service.get_project_metrics(project)
        self.assertIn("completion_percentage", metrics)
        self.assertIn("budget_utilized", metrics)
        self.assertIn("total_tasks", metrics)
