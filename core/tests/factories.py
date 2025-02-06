# core/tests/factories.py
import factory
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal
from core.models import Project, Task, Client


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
