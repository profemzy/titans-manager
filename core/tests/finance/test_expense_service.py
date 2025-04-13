from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from freezegun import freeze_time

from core.models import Expense
from core.services.finance.expense_service import ExpenseService
from core.tests.factories import ExpenseFactory, UserFactory


class ExpenseServiceTest(TestCase):
    def setUp(self):
        self.service = ExpenseService()
        self.user = UserFactory()

    def test_create_expense_success(self):
        expense = self.service.create_expense(
            title="Office Supplies",
            amount=Decimal("150.00"),
            category="utilities",
            submitted_by_id=self.user.id,
            payment_method="credit_card",
            date=date.today(),
            status="pending",
        )

        self.assertIsInstance(expense, Expense)
        self.assertEqual(expense.title, "Office Supplies")
        self.assertEqual(expense.amount, Decimal("150.00"))
        self.assertEqual(expense.submitted_by_id, self.user.id)

    def test_create_expense_negative_amount(self):
        with self.assertRaises(ValidationError):
            self.service.create_expense(
                title="Invalid Expense",
                amount=Decimal("-50.00"),
                category="utilities",
                submitted_by_id=self.user.id,
            )

    def test_create_expense_invalid_category(self):
        with self.assertRaises(ValidationError):
            self.service.create_expense(
                title="Test Expense",
                amount=Decimal("100.00"),
                category="invalid_category",
                submitted_by_id=self.user.id,
                payment_method="credit_card",
                date=date.today(),
            )

    @freeze_time("2025-02-07")
    def test_get_expense_summary(self):
        ExpenseFactory(amount=Decimal("100.00"), category="software", date=date.today())
        ExpenseFactory(amount=Decimal("200.00"), category="hardware", date=date.today())
        ExpenseFactory(amount=Decimal("300.00"), category="travel", date=date.today())
        ExpenseFactory(
            amount=Decimal("400.00"),
            category="utilities",
            date=date.today() - timedelta(days=40),
        )

        summary = self.service.get_expense_summary(
            start_date=date.today() - timedelta(days=30), end_date=date.today()
        )

        self.assertEqual(summary["total_amount"], Decimal("600.00"))

        categories = {
            item["category"]: item["total"] for item in summary["by_category"]
        }
        self.assertEqual(categories["software"], Decimal("100.00"))
        self.assertEqual(categories["hardware"], Decimal("200.00"))
        self.assertEqual(categories["travel"], Decimal("300.00"))

    def test_export_expense_csv(self):
        ExpenseFactory(
            title="Expense 1",
            amount=Decimal("100.00"),
            category="software",
            payment_method="credit_card",
            status="approved",
            vendor="Vendor A",
            date=date.today()
        )
        ExpenseFactory(
            title="Expense 2",
            amount=Decimal("200.00"),
            category="hardware",
            payment_method="cash",
            status="pending",
            vendor="Vendor B",
            date=date.today()
        )

        response = self.client.get("/titans-admin/core/expense/export-csv/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn('attachment; filename="expense_export.csv"', response["Content-Disposition"])

        content = response.content.decode("utf-8")
        self.assertIn("Expense 1", content)
        self.assertIn("Expense 2", content)
        self.assertIn("Vendor A", content)
        self.assertIn("Vendor B", content)
