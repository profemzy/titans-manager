from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db import OperationalError, connections
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import HealthCheckSerializer


class HealthCheckView(APIView):
    """
    API endpoint that checks system health.
    """

    permission_classes = [AllowAny]
    serializer_class = HealthCheckSerializer

    @method_decorator(cache_page(60))  # Cache for 1 minute
    def get(self, request):
        # Check database
        db_status = {}
        for db in connections.all():
            try:
                db.cursor()
                db_status[db.alias] = "healthy"
            except OperationalError:
                db_status[db.alias] = "unhealthy"

        # Check cache
        try:
            cache.set("health_check", "ok", 1)
            cache_status = cache.get("health_check") == "ok"
        except (ConnectionError, ValueError):
            cache_status = False

        # Add more comprehensive checks
        status_checks = {
            "database": db_status,
            "cache": cache_status,
            "status": (
                "ok"
                if all(status == "healthy" for status in db_status.values())
                and cache_status
                else "degraded"
            ),
            "timestamp": datetime.now(),
            "version": getattr(settings, "API_VERSION", "1.0.0"),
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
        }

        serializer = HealthCheckSerializer(status_checks)
        return Response(serializer.data)
