from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Invoice, User
from ..base import BaseService


class InvoiceService(BaseService[Invoice]):
    def __init__(self):
        super().__init__(Invoice)

    @transaction.atomic
    def create_invoice(self,
                      client_id: int,
                      project_id: int,
                      amount: Decimal,
                      due_date: date,
                      **kwargs) -> Invoice:
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
            **kwargs
        )

        return invoice

    @transaction.atomic
    def mark_as_paid(self, invoice: Invoice, user: User) -> Invoice:
        """Mark invoice as paid"""
        if invoice.status == 'paid':
            raise ValidationError("Invoice is already paid")

        return self.update(invoice, status='paid')

    def get_overdue_invoices(self) -> list:
        """Get all overdue invoices"""
        return self.model_class.objects.filter(
            status='sent',
            due_date__lt=date.today()
        )
