from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator

from core.models import User
from core.serializers import UserSerializer
from core.services.user_service import UserService

from ..base import BaseViewSet


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    service_class = UserService
    search_fields = ["username", "email", "first_name", "last_name", "employee_id"]
    ordering_fields = ["username", "date_joined", "last_login"]
    filterset_fields = ["role", "department", "status"]

    def get_queryset(self):
        return self.queryset.select_related("reports_to")

    @action(detail=True, methods=["get"])
    @method_decorator(cache_page(60 * 15))
    def workload(self, request, pk=None):
        """Get user's current workload"""
        user = self.get_object()
        service = self.service_class()
        workload = service.get_user_workload(user)
        return Response(workload)
