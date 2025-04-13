from decimal import Decimal
from django.core.management.base import BaseCommand


from core.models import Client, Expense, Income, Invoice, Project, User
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = "Seeds the database with realistic initial data"

    def handle(self, *args, **kwargs):
        # Create Users
        admin = User.objects.create_user(
            username="admin",
            email="admin@titansmanager.com",
            password="admin123",
            role="Admin",
        )
        manager = User.objects.create_user(
            username="manager",
            email="manager@titansmanager.com",
            password="manager123",
            role="Manager",
        )
        developer = User.objects.create_user(
            username="developer",
            email="dev@titansmanager.com",
            password="dev123",
            role="Developer",
        )

        # Create Clients
        clients = []
        for i in range(1, 4):
            client = Client.objects.create(
                name=f"Client {chr(64+i)}",
                email=f"client{chr(64+i)}@example.com",
                phone=f"123-456-78{i}0",
                company=f"Company {chr(64+i)}",
                address=f"{100+i} Main St",
            )
            clients.append(client)

        # Create Projects
        projects = []
        for i, client in enumerate(clients, start=1):
            project = Project.objects.create(
                name=f"Project {chr(87+i)}",
                description=f"Project {chr(87+i)} description",
                budget=Decimal(f"{random.randint(8000, 20000)}.00"),
                start_date=date.today() - timedelta(days=random.randint(30, 90)),
                end_date=date.today() + timedelta(days=random.randint(30, 90)),
                client=client,
            )
            projects.append(project)

        # Create Invoices
        invoices = []
        for project in projects:
            for j in range(1, 3):
                invoice = Invoice.objects.create(
                    client=project.client,
                    project=project,
                    amount=Decimal(f"{random.randint(2000, 7000)}.00"),
                    date=date.today() - timedelta(days=random.randint(10, 30)),
                    due_date=date.today() + timedelta(days=random.randint(10, 30)),
                    status=random.choice(["draft", "sent", "paid", "overdue"]),
                )
                invoices.append(invoice)

        # Create Income
        for invoice in invoices:
            if invoice.status == "paid":
                Income.objects.create(
                    amount=invoice.amount,
                    date=invoice.date + timedelta(days=random.randint(1, 5)),
                    client=invoice.client,
                    project=invoice.project,
                    invoice=invoice,
                )

        # Create Expenses
        expense_categories = ["software", "hardware", "travel", "office_supplies"]
        payment_methods = ["credit_card", "bank_transfer", "cash"]
        vendors = ["Vendor A", "Vendor B", "Vendor C", "Vendor D"]

        for _ in range(10):
            Expense.objects.create(
                title=random.choice(["Licenses", "Equipment", "Travel Expenses", "Office Supplies"]),
                amount=Decimal(f"{random.randint(100, 1500)}.00"),
                tax_amount=Decimal(f"{random.randint(10, 150)}.00"),
                date=date.today() - timedelta(days=random.randint(1, 60)),
                category=random.choice(expense_categories),
                tax_status=random.choice(["taxable", "non_taxable"]),
                payment_method=random.choice(payment_methods),
                description="Auto-generated expense for realistic data",
                status=random.choice(["paid", "pending", "approved"]),
                submitted_by=random.choice([admin, manager, developer]),
                vendor=random.choice(vendors),
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with realistic data!"))
