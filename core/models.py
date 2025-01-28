from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Employee')

# Client Model
class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

# Project Model
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    budget = models.DecimalField(max_digits=18, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name

# Task Model
class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    due_date = models.DateField()

    def __str__(self):
        return self.name

# Income Model
class Income(models.Model):
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='incomes')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='incomes')
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='incomes')

    def __str__(self):
        return f"Income: {self.amount} on {self.date}"

# Expense Model
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Software', 'Software'),
        ('Travel', 'Travel'),
        ('Salaries', 'Salaries'),
        ('Other', 'Other'),
    ]
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    receipt_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Expense: {self.amount} on {self.date}"

# Invoice Model
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Unpaid')

    def __str__(self):
        return f"Invoice: {self.amount} for {self.client.name}"
