from django.core.management.base import BaseCommand
from core.models import User, Client, Project, Task, Income, Expense, Invoice

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        # Create Users
        admin = User.objects.create_user(
            username='admin',
            email='admin@titansmanager.com',
            password='admin123',
            role='Admin'
        )
        manager = User.objects.create_user(
            username='manager',
            email='manager@titansmanager.com',
            password='manager123',
            role='Manager'
        )

        # Create Clients
        client_a = Client.objects.create(
            name='Client A',
            email='clientA@example.com',
            phone='123-456-7890',
            company='Company A',
            address='123 Main St'
        )

        # Create Projects
        project_x = Project.objects.create(
            name='Project X',
            description='Develop a new website',
            budget=10000.00,
            start_date='2023-10-01',
            end_date='2023-12-31',
            client=client_a
        )

        # Create Tasks
        task_1 = Task.objects.create(
            name='Design Homepage',
            description='Design the homepage layout',
            project=project_x,
            assigned_to=manager,
            status='Pending',
            due_date='2023-10-15'
        )

        # Create Invoices
        invoice_1 = Invoice.objects.create(
            client=client_a,
            project=project_x,
            amount=5000.00,
            date='2023-10-10',
            status='Unpaid'
        )

        # Create Income
        Income.objects.create(
            amount=5000.00,
            date='2023-10-10',
            client=client_a,
            project=project_x,
            invoice=invoice_1
        )

        # Create Expenses
        Expense.objects.create(
            title='Software Licenses',
            amount=1000.00,
            tax_amount=50.00,  # Assuming some tax
            date='2023-10-05',
            category='software',  # Match the choices in model
            tax_status='taxable',
            payment_method='credit_card',
            description='Purchased software licenses',
            status='paid',
            submitted_by=admin,  # Required field
            vendor='Software Vendor Inc.'
        )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
