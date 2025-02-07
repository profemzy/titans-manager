from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.filters import ExpenseFilter
from core.models import Expense
from core.serializers import ExpenseSerializer
from core.services.finance.expense_service import ExpenseService
from core.views.base import BaseViewSet


class ExpenseViewSet(BaseViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    service_class = ExpenseService
    filterset_class = ExpenseFilter
    search_fields = ["title", "vendor", "description"]
    ordering_fields = ["date", "amount", "category"]

    def get_queryset(self):
        return self.queryset.select_related("submitted_by", "approved_by")

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve an expense"""
        expense = self.get_object()
        service = self.service_class()

        try:
            approved_expense = service.approve_expense(expense, request.user)
            return Response(self.get_serializer(approved_expense).data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
