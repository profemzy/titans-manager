from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from freezegun import freeze_time

from core.models import Invoice
from core.services.finance.invoice_service import InvoiceService

from core.tests.factories import ClientFactory, ProjectFactory, UserFactory


class InvoiceServiceTest(TestCase):
    def setUp(self):
        self.service = InvoiceService()
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
        # Verify invoice number format: INV-YYYYMM-XXXX
        self.assertTrue(invoice.invoice_number.startswith("INV-202502-"))
        self.assertEqual(
            len(invoice.invoice_number), 15
        )  # INV-YYYYMM-XXXX = 15 chars (INV-202502-0001)

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
        """Test that invoice numbers are sequential within the same month"""
        due_date = date.today() + timedelta(days=30)

        # Create multiple invoices
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

        # Extract sequence numbers
        seq1 = int(invoice1.invoice_number.split("-")[-1])
        seq2 = int(invoice2.invoice_number.split("-")[-1])

        # Verify sequence
        self.assertEqual(seq2, seq1 + 1)
        self.assertTrue(invoice1.invoice_number.startswith("INV-202502-"))
        self.assertTrue(invoice2.invoice_number.startswith("INV-202502-"))

    def test_mark_as_paid(self):
        invoice = self.service.create_invoice(
            client_id=self.client.id,
            project_id=self.project.id,
            amount=Decimal("1500.00"),
            due_date=date.today() + timedelta(days=30),
        )

        # Mark as paid
        updated_invoice = self.service.mark_as_paid(invoice, self.user)
        self.assertEqual(updated_invoice.status, "paid")

        # Try to mark as paid again
        with self.assertRaises(ValidationError):
            self.service.mark_as_paid(updated_invoice, self.user)

    def test_get_overdue_invoices(self):
        # First create invoices with future due dates
        with freeze_time("2025-02-07"):
            # Create an invoice that will become overdue
            overdue_invoice = self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("1000.00"),
                due_date=date.today() + timedelta(days=5),
            )
            self.service.update(overdue_invoice, status="sent")

            # Create a future invoice that won't be overdue
            future_invoice = self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("2000.00"),
                due_date=date.today() + timedelta(days=15),
            )
            self.service.update(future_invoice, status="sent")

            # Create an invoice that will become overdue but is paid
            paid_invoice = self.service.create_invoice(
                client_id=self.client.id,
                project_id=self.project.id,
                amount=Decimal("3000.00"),
                due_date=date.today() + timedelta(days=5),
            )
            self.service.update(paid_invoice, status="paid")

        # Now move time forward to make some invoices overdue
        with freeze_time("2025-02-20"):  # Move time forward by 13 days

            overdue_invoices = self.service.get_overdue_invoices()

            # Check results
            self.assertEqual(len(overdue_invoices), 1)
            self.assertIn(
                overdue_invoice, overdue_invoices
            )  # Should be overdue and unpaid
            self.assertNotIn(future_invoice, overdue_invoices)  # Still in the future
            self.assertNotIn(paid_invoice, overdue_invoices)  # Overdue but paid
