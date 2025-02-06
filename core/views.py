from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import User, Client, Project, Task, Income, Expense, Invoice
from .serializers import (
    UserSerializer, ClientSerializer, ProjectSerializer,
    TaskSerializer, IncomeSerializer, ExpenseSerializer, InvoiceSerializer,
    HealthCheckSerializer
)
from .services.user_service import UserService
from .services.project_service import ProjectService
from .services.task_service import TaskService
from .services.client_service import ClientService
from .services.finance.income_service import IncomeService
from .services.finance.expense_service import ExpenseService
from .services.finance.invoice_service import InvoiceService
from .filters import ProjectFilter, TaskFilter, ExpenseFilter


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet providing common functionality
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Override to implement proper select_related and prefetch_related
        """
        return super().get_queryset()

    def handle_exception(self, exc):
        """
        Handle common exceptions
        """
        if isinstance(exc, ValidationError):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    service_class = UserService
    search_fields = ['username', 'email', 'first_name', 'last_name',
                     'employee_id']
    ordering_fields = ['username', 'date_joined', 'last_login']
    filterset_fields = ['role', 'department', 'status']

    def get_queryset(self):
        return self.queryset.select_related('reports_to')

    @action(detail=True, methods=['get'])
    @cache_page(60 * 15)  # Cache for 15 minutes
    def workload(self, request, pk=None):
        """Get user's current workload"""
        user = self.get_object()
        service = self.service_class()
        workload = service.get_user_workload(user)
        return Response(workload)


class ClientViewSet(BaseViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    service_class = ClientService
    search_fields = ['name', 'email', 'company']
    ordering_fields = ['name', 'created_at']
    filterset_fields = ['status', 'country']

    @action(detail=True, methods=['get'])
    def financial_summary(self, request, pk=None):
        """Get client's financial summary"""
        client = self.get_object()
        service = self.service_class()
        summary = service.get_financial_summary(client)
        return Response(summary)


class ProjectViewSet(BaseViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    service_class = ProjectService
    filterset_class = ProjectFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'budget']

    def get_queryset(self):
        return self.queryset.select_related(
            'client',
            'manager'
        ).prefetch_related('team_members')

    @action(detail=True, methods=['post'])
    def assign_team(self, request, pk=None):
        """Assign team members to project"""
        project = self.get_object()
        service = self.service_class()

        try:
            updated_project = service.assign_team_members(
                project,
                request.data.get('member_ids', [])
            )
            return Response(self.get_serializer(updated_project).data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    @cache_page(60 * 5)  # Cache for 5 minutes
    def metrics(self, request, pk=None):
        """Get project metrics"""
        project = self.get_object()
        service = self.service_class()
        metrics = service.get_project_metrics(project)
        return Response(metrics)


class TaskViewSet(BaseViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    service_class = TaskService
    filterset_class = TaskFilter
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['name', 'due_date', 'priority', 'status']

    def get_queryset(self):
        return self.queryset.select_related(
            'project',
            'assigned_to',
            'reviewer'
        ).prefetch_related('dependencies')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update task status"""
        task = self.get_object()
        service = self.service_class()

        try:
            updated_task = service.update_task_status(
                task,
                request.data.get('status'),
                request.user
            )
            return Response(self.get_serializer(updated_task).data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ExpenseViewSet(BaseViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    service_class = ExpenseService
    filterset_class = ExpenseFilter
    search_fields = ['title', 'vendor', 'description']
    ordering_fields = ['date', 'amount', 'category']

    def get_queryset(self):
        return self.queryset.select_related('submitted_by', 'approved_by')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an expense"""
        expense = self.get_object()
        service = self.service_class()

        try:
            approved_expense = service.approve_expense(
                expense,
                request.user
            )
            return Response(self.get_serializer(approved_expense).data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class IncomeViewSet(BaseViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    service_class = IncomeService
    search_fields = ['payment_reference', 'description']
    ordering_fields = ['date', 'amount', 'status']
    filterset_fields = ['payment_method', 'status', 'income_type']

    def get_queryset(self):
        return self.queryset.select_related('client', 'project', 'invoice')


class InvoiceViewSet(BaseViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    service_class = InvoiceService
    search_fields = ['invoice_number', 'notes']
    ordering_fields = ['date', 'due_date', 'amount', 'status']
    filterset_fields = ['status']

    def get_queryset(self):
        return self.queryset.select_related('client', 'project')

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        service = self.service_class()

        try:
            updated_invoice = service.mark_as_paid(invoice, request.user)
            return Response(self.get_serializer(updated_invoice).data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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
            cache.set('health_check', 'ok', 1)
            cache_status = cache.get('health_check') == 'ok'
        except (ConnectionError, ValueError):
            cache_status = False

        # Add more comprehensive checks
        status_checks = {
            'database': db_status,
            'cache': cache_status,
            'status': 'ok' if all(
                status == "healthy" for status in db_status.values()
            ) and cache_status else 'degraded',
            'timestamp': datetime.now(),
            'version': getattr(settings, 'API_VERSION', '1.0.0'),
            'environment': settings.ENVIRONMENT,
            'debug': settings.DEBUG
        }

        serializer = HealthCheckSerializer(status_checks)
        return Response(serializer.data)
