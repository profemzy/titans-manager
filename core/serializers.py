from rest_framework import serializers

from .models import Client, Expense, Income, Invoice, Project, Task, User


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for health check endpoint.
    """

    status = serializers.CharField(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True)
    database = serializers.DictField(read_only=True)
    cache = serializers.BooleanField(read_only=True)
    version = serializers.CharField(read_only=True)

    class Meta:
        swagger_schema_fields = {
            "description": "Health check endpoint for system status monitoring"
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Handles user data serialization and includes basic user information.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
        swagger_schema_fields = {
            "description": "User object for authentication and authorization"
        }


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client model.

    Includes all client information and related data.
    """

    total_projects = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Client
        fields = "__all__"
        swagger_schema_fields = {
            "description": "Client information including projects and revenue"
        }


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.

    Handles project data with status tracking and financial information.
    """

    completion_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        swagger_schema_fields = {
            "description": "Project details including status and progress"
        }


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.

    Manages task data with assignments and time tracking.
    """

    class Meta:
        model = Task
        fields = "__all__"
        swagger_schema_fields = {
            "description": "Task information with assignments and tracking"
        }


class IncomeSerializer(serializers.ModelSerializer):
    """
    Serializer for Income model.

    Handles income records with amount and date tracking.
    """

    class Meta:
        model = Income
        fields = "__all__"
        swagger_schema_fields = {
            "description": "Income records with financial tracking"
        }


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for Expense model.

    Manages expense records with categorization and payment tracking.
    """

    class Meta:
        model = Expense
        fields = "__all__"
        swagger_schema_fields = {"description": "Expense records with payment tracking"}


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Invoice model.

    Handles invoice data with status and payment tracking.
    """

    class Meta:
        model = Invoice
        fields = "__all__"
        swagger_schema_fields = {"description": "Invoice records with payment status"}
