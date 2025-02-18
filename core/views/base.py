from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet providing common functionality"""

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Override to implement proper select_related and prefetch_related"""
        return super().get_queryset()

    def get_object(self):
        """Get object for detail actions"""
        return get_object_or_404(self.queryset, pk=self.kwargs["pk"])

    def handle_exception(self, exc):
        """Handle common exceptions"""
        if isinstance(exc, ValidationError):
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)
