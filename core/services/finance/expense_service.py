from decimal import Decimal
from typing import Dict

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from core.models import Expense
from core.services.base import BaseService


class ExpenseService(BaseService[Expense]):
    def __init__(self):
        super().__init__(Expense)

    @transaction.atomic
    def create_expense(
        self, title: str, amount: Decimal, category: str, submitted_by_id: int, **kwargs
    ) -> Expense:
        """Create a new expense with proper validation."""
        if amount <= 0:
            raise ValidationError("Amount must be positive")

        expense = self.create(
            title=title,
            amount=amount,
            category=category,
            submitted_by_id=submitted_by_id,
            **kwargs
        )

        return expense

    def get_expense_summary(self, **filters) -> Dict[str, Decimal]:
        """Get expense summary with optional filters."""
        queryset = self.model_class.objects.all()

        if "start_date" in filters:
            queryset = queryset.filter(date__gte=filters["start_date"])
        if "end_date" in filters:
            queryset = queryset.filter(date__lte=filters["end_date"])
        if "category" in filters:
            queryset = queryset.filter(category=filters["category"])

        return {
            "total_amount": queryset.aggregate(total=Sum("amount"))["total"]
            or Decimal("0"),
            "by_category": queryset.values("category").annotate(total=Sum("amount")),
        }
