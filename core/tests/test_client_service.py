from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import Client
from core.services.client_service import ClientService
from .factories import ClientFactory, ProjectFactory


class ClientServiceTest(TestCase):
    def setUp(self):
        self.service = ClientService()
        self.client = ClientFactory()

    def test_get_financial_summary_empty(self):
        """Test financial summary for client with no data"""
        summary = self.service.get_financial_summary(self.client)

        self.assertEqual(summary["total_revenue"], Decimal("0"))
        self.assertEqual(summary["outstanding_amount"], Decimal("0"))
        self.assertEqual(summary["projects_count"], 0)
        self.assertEqual(summary["active_projects"], 0)
        self.assertEqual(summary["total_completed_projects"], 0)

    def test_get_financial_summary_with_data(self):
        """Test financial summary with projects and financial data"""
        # Create some projects with different statuses
        ProjectFactory(client=self.client, status="in_progress")
        ProjectFactory(client=self.client, status="in_progress")
        ProjectFactory(client=self.client, status="completed")

        summary = self.service.get_financial_summary(self.client)

        self.assertEqual(summary["projects_count"], 3)
        self.assertEqual(summary["active_projects"], 2)
        self.assertEqual(summary["total_completed_projects"], 1)

    def test_update_status(self):
        """Test updating client status"""
        # Test changing to inactive
        updated_client = self.service.update_status(self.client, "inactive")
        self.assertEqual(updated_client.status, "inactive")

        # Verify in database
        refreshed_client = Client.objects.get(pk=self.client.pk)
        self.assertEqual(refreshed_client.status, "inactive")

    def test_update_status_invalid_choice(self):
        """Test updating status with invalid value"""
        with self.assertRaises(ValidationError):
            self.service.update_status(self.client, "invalid_status")

    def test_update_status_valid_choices(self):
        """Test updating status with all valid choices"""
        valid_statuses = ["active", "inactive", "prospect", "former"]

        for status in valid_statuses:
            updated_client = self.service.update_status(self.client, status)
            self.assertEqual(updated_client.status, status)
            # Verify in database
            refreshed_client = Client.objects.get(pk=self.client.pk)
            self.assertEqual(refreshed_client.status, status)

    def test_model_properties(self):
        """Test client model properties"""
        client = ClientFactory(
            address="123 Test St",
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Test Country",
        )

        # Test full address
        expected_address = "123 Test St, Test City, Test State, 12345, Test Country"
        self.assertEqual(client.get_full_address(), expected_address)

        # Test total projects
        ProjectFactory(client=client, status="in_progress")
        ProjectFactory(client=client, status="completed")
        self.assertEqual(client.total_projects, 2)

        # Test string representation
        client_with_company = ClientFactory(name="Test Client", company="Test Company")
        self.assertEqual(str(client_with_company), "Test Client (Test Company)")

        client_without_company = ClientFactory(name="Test Client", company=None)
        self.assertEqual(str(client_without_company), "Test Client")

    def test_client_projects_metrics(self):
        """Test getting client projects metrics"""
        # Create projects with different statuses
        active_projects = [
            ProjectFactory(client=self.client, status="in_progress") for _ in range(2)
        ]
        completed_projects = [
            ProjectFactory(client=self.client, status="completed") for _ in range(3)
        ]

        # Test project counts
        total_projects = len(active_projects) + len(completed_projects)
        self.assertEqual(self.client.total_projects, total_projects)

        # Test project filtering
        self.assertEqual(
            self.client.projects.filter(status="in_progress").count(),
            len(active_projects),
        )
        self.assertEqual(
            self.client.projects.filter(status="completed").count(),
            len(completed_projects),
        )

        # Test financial summary reflects projects
        summary = self.service.get_financial_summary(self.client)
        self.assertEqual(summary["projects_count"], total_projects)
        self.assertEqual(summary["active_projects"], len(active_projects))
        self.assertEqual(summary["total_completed_projects"], len(completed_projects))
