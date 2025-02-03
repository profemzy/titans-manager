from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from datetime import datetime
from .serializers import HealthCheckSerializer
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
from rest_framework.response import Response
from .models import User, Client, Project, Task, Income, Expense, Invoice
from .serializers import (
    UserSerializer, ClientSerializer, ProjectSerializer,
    TaskSerializer, IncomeSerializer, ExpenseSerializer, InvoiceSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class HealthCheckView(APIView):
    """
    API endpoint that checks system health.
    """
    permission_classes = [AllowAny]
    serializer_class = HealthCheckSerializer

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
            cache.set('health_check', 'ok', 1)
            cache_status = cache.get('health_check') == 'ok'
        except:
            cache_status = False

        data = {
            'status': 'ok',
            'timestamp': datetime.now(),
            'database': db_status,
            'cache': cache_status,
            'version': getattr(settings, 'API_VERSION', '1.0.0')
        }

        serializer = HealthCheckSerializer(data)
        return Response(serializer.data)
