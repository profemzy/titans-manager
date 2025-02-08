from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import transaction
from freezegun import freeze_time

from core.models import Invoice, Income
from core.services.finance import invoice_service
from core.tests.factories import ClientFactory, ProjectFactory, UserFactory


class InvoiceServiceTest(TestCase):
    def setUp(self):
        self.service = invoice_service.InvoiceService()
        self.client = ClientFactory()
        self.project = ProjectFactory(client=self.client)
        self.user = UserFactory()

    @freeze_time("2025-02-07")
    def test_create_invoice_success(self):
        due_date = date.today() + timedelta(days=30)
        invoice = self.service.create_invoice(
            client_id=self.client.id,
            project_id=self.project.id,
            amount=Decimal("1500.00"),
            due_date=due_date,
        )

        self.assertIsInstance(invoice, Invoice)
        self.assertEqual(invoice.amount, Decimal("1500.00"))
        self.assertEqual(invoice.client_id, self.client.id)
        self.assertEqual(invoice.project_id, self.project.id)
        self.assertEqual(invoice.status, "draft")
        self.assertEqual(invoice.date, date.today())
        self.assertTrue(invoice.invoice_number.startswith("INV-202502-"))
        self.assertEqual(len(invoice.invoice_number), 15)

    def test_create_invoice_negative_amount(self):
        due_date = date.today() + timedelta(days=30)
        with self.assertRaises(ValidationError):
            self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("-500.00"),
                due_date=due_date,
            )

    def test_create_invoice_past_due_date(self):
        past_due_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("1500.00"),
                due_date=past_due_date,
            )

    @freeze_time("2025-02-07")
    def test_invoice_number_sequence(self):
        due_date = date.today() + timedelta(days=30)

        invoice1 = self.service.create_invoice(
            client_id=self.client.id,
            project_id=self.project.id,
            amount=Decimal("1000.00"),
            due_date=due_date,
        )
        invoice2 = self.service.create_invoice(
            client_id=self.client.id,
            project_id=self.project.id,
            amount=Decimal("2000.00"),
            due_date=due_date,
        )

        seq1 = int(invoice1.invoice_number.split("-")[-1])
        seq2 = int(invoice2.invoice_number.split("-")[-1])

        self.assertEqual(seq2, seq1 + 1)
        self.assertTrue(invoice1.invoice_number.startswith("INV-202502-"))
        self.assertTrue(invoice2.invoice_number.startswith("INV-202502-"))

    @freeze_time("2025-02-07")
    def test_mark_as_paid_creates_income(self):
        # Create an invoice
        invoice = self.service.create_invoice(
            client_id=self.client.id,
            project_id=self.project.id,
            amount=Decimal("1500.00"),
            due_date=date.today() + timedelta(days=30),
        )

        # Mark as paid
        with transaction.atomic():
            updated_invoice, income_record = self.service.mark_as_paid(
                invoice, self.user
            )

        # Refresh from database to ensure persistence
        updated_invoice.refresh_from_db()

        # Verify invoice status
        self.assertEqual(updated_invoice.status, "paid")

        # Query the database directly to verify income record
        income = Income.objects.filter(invoice=updated_invoice).first()
        self.assertIsNotNone(income)

        # Refresh income from database to ensure all fields are loaded
        income.refresh_from_db()

        # Verify all income fields
        self.assertEqual(income.amount, invoice.amount)
        self.assertEqual(income.client_id, invoice.client_id)
        self.assertEqual(income.project_id, invoice.project_id)
        self.assertEqual(income.status, "received")
        self.assertEqual(income.income_type, "project_payment")
        self.assertEqual(income.payment_method, "bank_transfer")
        self.assertEqual(income.date, date.today())
        self.assertEqual(income.received_date, date.today())
        self.assertEqual(
            income.description, f"Payment for Invoice #{invoice.invoice_number}"
        )

        # Verify the relationship is bi-directional
        self.assertEqual(income.invoice_id, updated_invoice.id)
        self.assertEqual(list(updated_invoice.incomes.all()), [income])

    def test_mark_as_paid_twice_fails(self):
        invoice = self.service.create_invoice(
            client_id=self.client.id,
            project_id=self.project.id,
            amount=Decimal("1500.00"),
            due_date=date.today() + timedelta(days=30),
        )

        # Mark as paid first time
        self.service.mark_as_paid(invoice, self.user)

        # Verify one income record exists
        self.assertEqual(Income.objects.filter(invoice=invoice).count(), 1)

        # Try to mark as paid again
        with self.assertRaises(ValidationError):
            self.service.mark_as_paid(invoice, self.user)

        # Verify still only one income record exists
        self.assertEqual(Income.objects.filter(invoice=invoice).count(), 1)

    def test_get_overdue_invoices(self):
        with freeze_time("2025-02-07"):
            overdue_invoice = self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("1000.00"),
                due_date=date.today() + timedelta(days=5),
            )
            self.service.update(overdue_invoice, status="sent")

            future_invoice = self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("2000.00"),
                due_date=date.today() + timedelta(days=15),
            )
            self.service.update(future_invoice, status="sent")

            paid_invoice = self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("3000.00"),
                due_date=date.today() + timedelta(days=5),
            )
            self.service.mark_as_paid(paid_invoice, self.user)

        with freeze_time("2025-02-20"):
            overdue_invoices = self.service.get_overdue_invoices()

            self.assertEqual(len(overdue_invoices), 1)
            self.assertIn(overdue_invoice, overdue_invoices)
            self.assertNotIn(future_invoice, overdue_invoices)
            self.assertNotIn(paid_invoice, overdue_invoices)
