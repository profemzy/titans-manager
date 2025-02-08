from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from freezegun import freeze_time

from core.models import Invoice
from .factories import (
    ClientFactory,
    ExpenseFactory,
    IncomeFactory,
    ProjectFactory,
    TaskFactory,
    UserFactory,
)


class ProjectModelTest(TestCase):
    def setUp(self):
        self.client = ClientFactory()
        self.manager = UserFactory()
        self.project = ProjectFactory(
            client=self.client,
            manager=self.manager,
            budget=Decimal("10000.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

    def test_completion_percentage(self):
        # Create 4 tasks, 2 completed and 2 pending
        TaskFactory.create_batch(
            2,
            project=self.project,
            status="Completed",  # Changed to match model's choice
        )
        TaskFactory.create_batch(
            2, project=self.project, status="Pending"  # Changed to match model's choice
        )

        self.assertEqual(self.project.completion_percentage, 50)

    def test_completion_percentage_no_tasks(self):
        self.assertEqual(self.project.completion_percentage, 0)

    def test_budget_utilized(self):
        # Create expenses totaling 2500
        expense1 = ExpenseFactory(amount=Decimal("1500.00"))
        expense1.projects.set([self.project])

        expense2 = ExpenseFactory(amount=Decimal("1000.00"))
        expense2.projects.set([self.project])

        # Update project's actual cost
        self.project.actual_cost = Decimal("2500.00")
        self.project.save()

        # Budget utilized should be 25% (2500/10000 * 100)
        self.assertEqual(self.project.budget_utilized, 25)

    def test_profit_margin(self):
        # Create income of 10000 and expenses of 6000
        IncomeFactory(project=self.project, amount=Decimal("10000.00"))
        expense = ExpenseFactory(amount=Decimal("6000.00"))
        expense.projects.set([self.project])

        # Profit margin should be 40%
        self.assertEqual(self.project.profit_margin, 40)

    def test_profit_margin_no_income(self):
        expense = ExpenseFactory(amount=Decimal("1000.00"))
        expense.projects.set([self.project])
        self.assertEqual(self.project.profit_margin, 0)

    @freeze_time("2025-02-07")
    def test_is_overdue(self):
        # Create a project due yesterday
        overdue_project = ProjectFactory(
            end_date=date.today() - timedelta(days=1), status="in_progress"
        )
        self.assertTrue(overdue_project.is_overdue)

        # Create a project due tomorrow
        future_project = ProjectFactory(
            end_date=date.today() + timedelta(days=1), status="in_progress"
        )
        self.assertFalse(future_project.is_overdue)

        # Completed projects should not be overdue
        completed_project = ProjectFactory(
            end_date=date.today() - timedelta(days=1), status="completed"
        )
        self.assertFalse(completed_project.is_overdue)


class InvoiceModelTest(TestCase):
    def setUp(self):
        self.client = ClientFactory()
        self.project = ProjectFactory(client=self.client)

    @freeze_time("2025-02-07")
    def test_invoice_number_generation(self):
        invoice1 = Invoice.objects.create(
            client=self.client,
            project=self.project,
            amount=Decimal("1000.00"),
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
        )

        # First invoice of the month should end with 0001
        self.assertEqual(invoice1.invoice_number, "INV-202502-0001")

        invoice2 = Invoice.objects.create(
            client=self.client,
            project=self.project,
            amount=Decimal("2000.00"),
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
        )

        # Second invoice should end with 0002
        self.assertEqual(invoice2.invoice_number, "INV-202502-0002")

    @freeze_time("2025-02-07")
    def test_invoice_number_uniqueness(self):
        # Create invoices in the same month and verify they have unique numbers
        invoices = []
        for _ in range(5):
            invoice = Invoice.objects.create(
                client=self.client,
                project=self.project,
                amount=Decimal("1000.00"),
                date=date.today(),
                due_date=date.today() + timedelta(days=30),
            )
            self.assertNotIn(
                invoice.invoice_number, [i.invoice_number for i in invoices]
            )
            invoices.append(invoice)


class UserModelTest(TestCase):
    @freeze_time("2025-02-07")
    def test_employee_id_generation(self):
        # Test employee ID for different departments
        dev_user = UserFactory(department="development", role="Employee")
        self.assertTrue(dev_user.employee_id.startswith("25DE"))

        sales_user = UserFactory(department="sales", role="Employee")
        self.assertTrue(sales_user.employee_id.startswith("25SA"))

    def test_employee_id_sequence(self):
        # Test that sequential employees get sequential numbers
        department = "development"
        users = [UserFactory(department=department, role="Employee") for _ in range(3)]

        # Extract sequence numbers
        sequences = [int(user.employee_id[-3:]) for user in users]
        # Verify they are sequential
        self.assertEqual(sequences[1], sequences[0] + 1)
        self.assertEqual(sequences[2], sequences[1] + 1)

    @freeze_time("2025-02-07 12:00:00+00:00")
    def test_get_total_hours_worked(self):
        from django.utils import timezone
        from datetime import datetime, time

        user = UserFactory()
        now = timezone.now()

        # Create start and end datetime objects (start of day and end of day)
        start_datetime = timezone.make_aware(
            datetime.combine(now.date() - timedelta(days=1), time.min)
        )
        end_datetime = timezone.make_aware(
            datetime.combine(now.date() + timedelta(days=1), time.max)
        )

        # Create completed tasks with different hours
        TaskFactory(
            assigned_to=user,
            status="Completed",
            actual_hours=Decimal("4.5"),
            completed_at=now,
        )
        TaskFactory(
            assigned_to=user,
            status="Completed",
            actual_hours=Decimal("3.5"),
            completed_at=now,
        )
        # Create a pending task (shouldn't be counted)
        TaskFactory(assigned_to=user, status="Pending", actual_hours=Decimal("2.0"))

        total_hours = user.get_total_hours_worked(
            start_date=start_datetime, end_date=end_datetime
        )
        self.assertEqual(total_hours, Decimal("8.0"))
