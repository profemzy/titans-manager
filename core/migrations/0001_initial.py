# Generated by Django 5.1.5 on 2025-01-29 05:08

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('company', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('Admin', 'Admin'), ('Manager', 'Manager'), ('Employee', 'Employee')], default='Employee', max_length=50)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=18)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='core.client')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=18)),
                ('date', models.DateField()),
                ('status', models.CharField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid', max_length=50)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='core.client')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='core.project')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Pending', max_length=50)),
                ('due_date', models.DateField()),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.project')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=18)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=18)),
                ('category', models.CharField(choices=[('rent', 'Rent/Lease'), ('utilities', 'Utilities'), ('software', 'Software/Tools'), ('hardware', 'Hardware/Equipment'), ('travel', 'Travel'), ('salaries', 'Salaries/Payroll'), ('marketing', 'Marketing'), ('office', 'Office Supplies'), ('insurance', 'Insurance'), ('taxes', 'Taxes'), ('maintenance', 'Maintenance'), ('professional', 'Professional Services'), ('training', 'Training/Education'), ('other', 'Other')], max_length=100)),
                ('tax_status', models.CharField(choices=[('taxable', 'Taxable'), ('non_taxable', 'Non-Taxable')], default='taxable', max_length=20)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('credit_card', 'Credit Card'), ('debit_card', 'Debit Card'), ('bank_transfer', 'Bank Transfer'), ('cheque', 'Cheque'), ('paypal', 'PayPal'), ('other', 'Other')], max_length=50)),
                ('payment_reference', models.CharField(blank=True, help_text='Reference number, cheque number, or transaction ID', max_length=100, null=True)),
                ('date', models.DateField(help_text='Date of expense')),
                ('due_date', models.DateField(blank=True, help_text='Due date for payment if applicable', null=True)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('is_recurring', models.BooleanField(default=False)),
                ('recurring_frequency', models.CharField(choices=[('none', 'Not Recurring'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], default='none', max_length=20)),
                ('recurring_end_date', models.DateField(blank=True, null=True)),
                ('receipt', models.FileField(blank=True, null=True, upload_to='receipts/%Y/%m/')),
                ('invoice_number', models.CharField(blank=True, max_length=100, null=True)),
                ('vendor', models.CharField(blank=True, max_length=200, null=True)),
                ('vendor_tax_number', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_expenses', to=settings.AUTH_USER_MODEL)),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_expenses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
                'indexes': [models.Index(fields=['date'], name='core_expens_date_d957f6_idx'), models.Index(fields=['category'], name='core_expens_categor_358de0_idx'), models.Index(fields=['status'], name='core_expens_status_32e345_idx'), models.Index(fields=['is_recurring'], name='core_expens_is_recu_9e3925_idx')],
            },
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=18)),
                ('date', models.DateField()),
                ('expected_date', models.DateField(blank=True, null=True)),
                ('received_date', models.DateField(blank=True, null=True)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('cheque', 'Cheque'), ('bank_transfer', 'Bank Transfer'), ('credit_card', 'Credit Card'), ('paypal', 'PayPal'), ('other', 'Other')], default='bank_transfer', max_length=50)),
                ('payment_reference', models.CharField(blank=True, help_text='Transaction ID, cheque number, etc.', max_length=100, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('received', 'Received'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('income_type', models.CharField(choices=[('project_payment', 'Project Payment'), ('retainer', 'Retainer Fee'), ('consultation', 'Consultation'), ('maintenance', 'Maintenance'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incomes', to='core.client')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incomes', to='core.invoice')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incomes', to='core.project')),
            ],
            options={
                'verbose_name': 'Income',
                'verbose_name_plural': 'Income',
                'ordering': ['-date', '-created_at'],
                'indexes': [models.Index(fields=['date'], name='core_income_date_790cb6_idx'), models.Index(fields=['status'], name='core_income_status_f84b0b_idx'), models.Index(fields=['income_type'], name='core_income_income__06ca8a_idx')],
            },
        ),
    ]
