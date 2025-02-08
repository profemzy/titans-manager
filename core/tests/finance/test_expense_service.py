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
            category="utilities",  # Using a standard category
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
                category="invalid_category",  # Category not in CATEGORY_CHOICES
                submitted_by_id=self.user.id,
                payment_method="credit_card",
                date=date.today(),
            )

    @freeze_time("2025-02-07")
    def test_get_expense_summary(self):
        # Create test expenses across different categories
        ExpenseFactory(amount=Decimal("100.00"), category="software", date=date.today())
        ExpenseFactory(amount=Decimal("200.00"), category="hardware", date=date.today())
        ExpenseFactory(amount=Decimal("300.00"), category="travel", date=date.today())
        # Create an expense for previous month (shouldn't be included in filtered results)
        ExpenseFactory(
            amount=Decimal("400.00"),
            category="utilities",
            date=date.today() - timedelta(days=40),
        )

        # Test summary with date filter
        summary = self.service.get_expense_summary(
            start_date=date.today() - timedelta(days=30), end_date=date.today()
        )

        self.assertEqual(summary["total_amount"], Decimal("600.00"))

        # Convert categories summary to dict for easier testing
        categories = {
            item["category"]: item["total"] for item in summary["by_category"]
        }
        self.assertEqual(categories["software"], Decimal("100.00"))
        self.assertEqual(categories["hardware"], Decimal("200.00"))
        self.assertEqual(categories["travel"], Decimal("300.00"))
