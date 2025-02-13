from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet as BaseViewSet  # Keeping your existing import

from core.models import Client
from core.serializers import ClientSerializer
from core.services.client_service import ClientService


class ClientViewSet(BaseViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    service_class = ClientService
    search_fields = ["name", "email", "company"]
    ordering_fields = ["name", "created_at"]
    filterset_fields = ["status", "country"]

    def get_object(self):
        """Add get_object method to work with the detail action"""
        return Client.objects.get(pk=self.kwargs["pk"])

    @action(detail=True, methods=["get"])
    def financial_summary(self, request, pk=None):
        """Get client's financial summary"""
        client = self.get_object()
        service = self.service_class()
        summary = service.get_financial_summary(client)
        return Response(summary)
