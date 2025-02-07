from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet as BaseViewSet

from core.models import Invoice
from core.serializers import InvoiceSerializer
from core.services.finance.invoice_service import InvoiceService


class InvoiceViewSet(BaseViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    service_class = InvoiceService
    search_fields = ["invoice_number", "notes"]
    ordering_fields = ["date", "due_date", "amount", "status"]
    filterset_fields = ["status"]

    def get_queryset(self):
        return self.queryset.select_related("client", "project")

    @action(detail=True, methods=["post"])
    def mark_as_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        service = self.service_class()

        try:
            updated_invoice = service.mark_as_paid(invoice, request.user)
            return Response(self.get_serializer(updated_invoice).data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
