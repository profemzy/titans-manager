from datetime import date, timedelta
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from core.models import Client, Project, Task, Expense, Income


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True


class ClientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Client

    name = factory.Faker("company")
    email = factory.Faker("company_email")
    status = "active"


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    code = factory.Sequence(lambda n: f"PRJ{n:04d}")  # Generates PRJ0001, PRJ0002, etc.
    client = factory.SubFactory(ClientFactory)
    manager = factory.SubFactory(UserFactory)
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    budget = factory.LazyFunction(lambda: Decimal("10000.00"))
    status = "planning"
    priority = "medium"


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    name = factory.Sequence(lambda n: f"Task {n}")
    project = factory.SubFactory(ProjectFactory)
    assigned_to = factory.SubFactory(UserFactory)
    status = "pending"
    priority = "medium"
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))


class ExpenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Expense

    title = factory.Sequence(lambda n: f"Expense {n}")
    amount = factory.LazyFunction(lambda: Decimal("100.00"))
    category = "utilities"  # Changed from office_supplies to utilities
    payment_method = "credit_card"
    date = factory.LazyFunction(date.today)
    status = "pending"
    submitted_by = factory.SubFactory(UserFactory)


class IncomeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Income

    amount = factory.LazyFunction(lambda: Decimal("1000.00"))
    date = factory.LazyFunction(date.today)
    client = factory.SubFactory(ClientFactory)
    project = factory.SubFactory(ProjectFactory)
    payment_method = "bank_transfer"
    status = "pending"
    income_type = "project_payment"
