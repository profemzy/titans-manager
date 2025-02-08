from datetime import date
from decimal import Decimal
from typing import Tuple

from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Invoice, User, Income
from ..base import BaseService


__all__ = ["InvoiceService"]


class InvoiceService(BaseService[Invoice]):
    def __init__(self):
        super().__init__(Invoice)
        # Import here to avoid circular dependency
        from core.services.finance.income_service import IncomeService

        self._income_service = None
        self._income_service_class = IncomeService

    @property
    def income_service(self):
        if self._income_service is None:
            self._income_service = self._income_service_class()
        return self._income_service

    @transaction.atomic
    def create_invoice(
        self, client_id: int, project_id: int, amount: Decimal, due_date: date, **kwargs
    ) -> Invoice:
        """Create a new invoice"""
        if amount <= 0:
            raise ValidationError("Amount must be positive")

        if due_date < date.today():
            raise ValidationError("Due date cannot be in the past")

        invoice = self.create(
            client_id=client_id,
            project_id=project_id,
            amount=amount,
            due_date=due_date,
            date=date.today(),
            **kwargs,
        )

        return invoice

    @transaction.atomic
    def mark_as_paid(self, invoice: Invoice, user: User) -> Tuple[Invoice, Income]:
        """
        Mark invoice as paid and create corresponding income record

        Args:
            invoice: The invoice to mark as paid
            user: The user performing the action

        Returns:
            A tuple containing (updated_invoice, created_income)

        Raises:
            ValidationError: If the invoice is already paid or if payment processing fails
        """
        if invoice.status == "paid":
            raise ValidationError("Invoice is already paid")

        try:
            today = date.today()
            # Create income record using IncomeService with explicit parameters
            income = self.income_service.record_income(
                client_id=invoice.client.id,
                project_id=invoice.project.id,
                amount=invoice.amount,
                income_type="project_payment",
                payment_method="bank_transfer",
                date=today,
                received_date=today,
                status="received",
                description=f"Payment for Invoice #{invoice.invoice_number}",
                invoice=invoice,
            )

            # Update invoice status
            updated_invoice = self.update(invoice, status="paid")

            return updated_invoice, income

        except Exception as e:
            raise ValidationError(f"Failed to process payment: {str(e)}")

    def get_overdue_invoices(self) -> list[Invoice]:
        """Get all overdue invoices"""
        return self.model_class.objects.filter(status="sent", due_date__lt=date.today())
