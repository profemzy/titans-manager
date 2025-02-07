from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet as BaseViewSet

from core.filters import TaskFilter
from core.models import Task
from core.serializers import TaskSerializer
from core.services.task_service import TaskService


class TaskViewSet(BaseViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    service_class = TaskService
    filterset_class = TaskFilter

    def get_queryset(self):
        return self.queryset.select_related(
            "project", "assigned_to", "reviewer"
        ).prefetch_related("dependencies")

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update task status"""
        task = self.get_object()
        service = self.service_class()

        try:
            updated_task = service.update_task_status(
                task, request.data.get("status"), request.user
            )
            return Response(self.get_serializer(updated_task).data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
