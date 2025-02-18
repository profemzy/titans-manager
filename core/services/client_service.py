from decimal import Decimal
from typing import Any, Dict

from django.db.models import Sum
from django.core.exceptions import ValidationError

from core.models import Client

from .base import BaseService


class ClientService(BaseService[Client]):
    def __init__(self):
        super().__init__(Client)

    def get_financial_summary(self, client: Client) -> Dict[str, Any]:
        """Get client's financial summary"""
        incomes = client.incomes.all()
        invoices = client.invoices.all()
        projects = client.projects.all()

        return {
            "total_revenue": incomes.aggregate(total=Sum("amount"))["total"]
            or Decimal("0"),
            "outstanding_amount": invoices.filter(status="sent").aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0"),
            "projects_count": projects.count(),
            "active_projects": projects.filter(status="in_progress").count(),
            "total_completed_projects": projects.filter(status="completed").count(),
        }

    def update_status(self, client: Client, new_status: str) -> Client:
        """
        Update client's status

        Args:
            client: Client instance to update
            new_status: New status value

        Raises:
            ValidationError: If status is not one of the valid choices
        """
        valid_statuses = dict(Client.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            raise ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        client.status = new_status
        client.save()
        return client
