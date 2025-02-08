from datetime import date
from decimal import Decimal
from typing import Any, Dict, List

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from core.models import Income
from ..base import BaseService

__all__ = ["IncomeService"]


class IncomeService(BaseService[Income]):
    """Service class for managing Income records"""

    def __init__(self):
        super().__init__(Income)

    @transaction.atomic
    def record_income(
        self,
        client_id: int,
        project_id: int,
        amount: Decimal,
        income_type: str,
        payment_method: str,
        **kwargs
    ) -> Income:
        """Record a new income"""
        if amount <= 0:
            raise ValidationError("Amount must be positive")

        # Create income record without date if it's in kwargs
        income_data = {
            "client_id": client_id,
            "project_id": project_id,
            "amount": amount,
            "income_type": income_type,
            "payment_method": payment_method,
            "status": kwargs.get("status", "pending"),
            "received_date": kwargs.get("received_date"),
            "description": kwargs.get("description"),
            "notes": kwargs.get("notes"),
            "invoice": kwargs.get("invoice"),
        }

        # Only add date if not provided in kwargs
        if "date" not in kwargs:
            income_data["date"] = date.today()
        else:
            income_data["date"] = kwargs["date"]

        # Filter out None values to allow model defaults to apply
        income_data = {k: v for k, v in income_data.items() if v is not None}

        income = self.create(**income_data)
        return income

    def get_income_summary(
        self, start_date: date = None, end_date: date = None
    ) -> Dict[str, Any]:
        """Get income summary for a date range"""
        queryset = self.model_class.objects.all()

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return {
            "total_amount": queryset.aggregate(total=Sum("amount"))["total"]
            or Decimal("0"),
            "by_type": queryset.values("income_type").annotate(total=Sum("amount")),
            "by_payment_method": queryset.values("payment_method").annotate(
                total=Sum("amount")
            ),
        }

    def get_pending_payments(self) -> List[Income]:
        """Get all pending income payments"""
        return self.model_class.objects.filter(status="pending").order_by(
            "expected_date"
        )
