from core.models import Income
from core.serializers import IncomeSerializer
from core.services.finance.income_service import IncomeService
from core.views.base import BaseViewSet


class IncomeViewSet(BaseViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    service_class = IncomeService
    search_fields = ["payment_reference", "description"]
    ordering_fields = ["date", "amount", "status"]
    filterset_fields = ["payment_method", "status", "income_type"]

    def get_queryset(self):
        return self.queryset.select_related("client", "project", "invoice")
