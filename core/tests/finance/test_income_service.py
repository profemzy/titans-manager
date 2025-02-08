from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from freezegun import freeze_time

from core.models import Income
from core.services.finance.income_service import IncomeService
from core.tests.factories import ClientFactory, ProjectFactory, IncomeFactory


class IncomeServiceTest(TestCase):
    def setUp(self):
        self.service = IncomeService()
        self.client = ClientFactory()
        self.project = ProjectFactory(client=self.client)

    def test_record_income_success(self):
        income = self.service.record_income(
            client_id=self.client.id,
            project_id=self.project.id,
            amount=Decimal("1000.00"),
            income_type="project_payment",
            payment_method="bank_transfer",
        )

        self.assertIsInstance(income, Income)
        self.assertEqual(income.amount, Decimal("1000.00"))
        self.assertEqual(income.client_id, self.client.id)
        self.assertEqual(income.project_id, self.project.id)
        self.assertEqual(income.status, "pending")

    def test_record_income_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.service.record_income(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("-500.00"),
                income_type="project_payment",
                payment_method="bank_transfer",
            )

    @freeze_time("2025-02-07")
    def test_get_income_summary(self):
        # Create test incomes with different dates and types
        IncomeFactory(
            client=self.client,
            project=self.project,
            amount=Decimal("1000.00"),
            income_type="project_payment",
            date=date.today(),
        )
        IncomeFactory(
            client=self.client,
            project=self.project,
            amount=Decimal("500.00"),
            income_type="consultation",
            date=date.today(),
        )
        # Create an income from previous month (shouldn't be included in filtered results)
        IncomeFactory(
            client=self.client,
            project=self.project,
            amount=Decimal("750.00"),
            income_type="project_payment",
            date=date.today() - timedelta(days=40),
        )

        # Test summary with date filter
        summary = self.service.get_income_summary(
            start_date=date.today() - timedelta(days=30), end_date=date.today()
        )

        self.assertEqual(summary["total_amount"], Decimal("1500.00"))

        # Convert income types summary to dict for easier testing
        by_type = {item["income_type"]: item["total"] for item in summary["by_type"]}
        self.assertEqual(by_type["project_payment"], Decimal("1000.00"))
        self.assertEqual(by_type["consultation"], Decimal("500.00"))

    def test_get_pending_payments(self):
        # Create some test incomes with different statuses
        pending_income1 = IncomeFactory(
            client=self.client,
            project=self.project,
            status="pending",
            expected_date=date.today(),
        )
        pending_income2 = IncomeFactory(
            client=self.client,
            project=self.project,
            status="pending",
            expected_date=date.today() + timedelta(days=1),
        )
        # Create a received income (shouldn't be included in pending payments)
        IncomeFactory(client=self.client, project=self.project, status="received")

        pending_payments = self.service.get_pending_payments()

        self.assertEqual(len(pending_payments), 2)
        self.assertIn(pending_income1, pending_payments)
        self.assertIn(pending_income2, pending_payments)
        # Verify ordering by expected_date
        self.assertEqual(list(pending_payments), [pending_income1, pending_income2])
