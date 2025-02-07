from django.core.exceptions import ValidationError
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.filters import ProjectFilter
from core.models import Project
from core.serializers import ProjectSerializer
from core.services.project_service import ProjectService

from ..base import BaseViewSet


class ProjectViewSet(BaseViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    service_class = ProjectService
    filterset_class = ProjectFilter
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "start_date", "end_date", "budget"]

    def get_queryset(self):
        return self.queryset.select_related("client", "manager").prefetch_related(
            "team_members"
        )

    @action(detail=True, methods=["post"])
    def assign_team(self, request, pk=None):
        """Assign team members to project"""
        project = self.get_object()
        service = self.service_class()
        try:
            updated_project = service.assign_team_members(
                project, request.data.get("member_ids", [])
            )
            return Response(self.get_serializer(updated_project).data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    @cache_page(60 * 5)  # Cache for 5 minutes
    def metrics(self, request, pk=None):
        """Get project metrics"""
        project = self.get_object()
        service = self.service_class()
        metrics = service.get_project_metrics(project)
        return Response(metrics)
