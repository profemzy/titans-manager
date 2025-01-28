from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Client, Project, Task, Income, Expense, Invoice
from .serializers import (
    UserSerializer, ClientSerializer, ProjectSerializer,
    TaskSerializer, IncomeSerializer, ExpenseSerializer, InvoiceSerializer
)

# User Viewset
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Client Viewset
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

# Project Viewset
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

# Task Viewset
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

# Income Viewset
class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

# Expense Viewset
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

# Invoice Viewset
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
