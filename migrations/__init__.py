from decimal import Decimal

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

from core.models.finance import CATEGORY_CHOICES


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("Admin", "Admin"),
                            ("Manager", "Manager"),
                            ("Employee", "Employee"),
                            ("Contractor", "Contractor"),
                            ("Intern", "Intern"),
                        ],
                        default="Employee",
                        max_length=50,
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("management", "Management"),
                            ("development", "Development"),
                            ("design", "Design"),
                            ("marketing", "Marketing"),
                            ("sales", "Sales"),
                            ("hr", "Human Resources"),
                            ("finance", "Finance"),
                            ("other", "Other"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("on_leave", "On Leave"),
                            ("inactive", "Inactive"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=17,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                                regex="^\\+?1?\\d{9,15}$",
                            )
                        ],
                    ),
                ),
                (
                    "emergency_contact",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "emergency_phone",
                    models.CharField(
                        blank=True,
                        max_length=17,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
                                regex="^\\+?1?\\d{9,15}$",
                            )
                        ],
                    ),
                ),
                (
                    "employee_id",
                    models.CharField(blank=True, max_length=20, null=True, unique=True),
                ),
                ("job_title", models.CharField(blank=True, max_length=100, null=True)),
                ("hire_date", models.DateField(blank=True, null=True)),
                (
                    "hourly_rate",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "skills",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated list of skills",
                        max_length=500,
                        null=True,
                    ),
                ),
                ("certifications", models.TextField(blank=True, null=True)),
                (
                    "working_hours",
                    models.DecimalField(
                        decimal_places=2,
                        default=40.0,
                        help_text="Weekly working hours",
                        max_digits=4,
                    ),
                ),
                (
                    "time_zone",
                    models.CharField(
                        default="UTC",
                        help_text="User's primary timezone",
                        max_length=50,
                    ),
                ),
                ("last_password_change", models.DateTimeField(blank=True, null=True)),
                ("login_attempts", models.IntegerField(default=0)),
                ("last_login_attempt", models.DateTimeField(blank=True, null=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "reports_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="subordinates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ["username"],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("company", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "alternate_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "mobile_phone",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("website", models.URLField(blank=True, null=True)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
                ("city", models.CharField(blank=True, max_length=100, null=True)),
                ("state", models.CharField(blank=True, max_length=100, null=True)),
                ("postal_code", models.CharField(blank=True, max_length=20, null=True)),
                ("country", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "tax_number",
                    models.CharField(
                        blank=True, help_text="VAT/GST/Tax ID", max_length=50, null=True
                    ),
                ),
                ("industry", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("inactive", "Inactive"),
                            ("prospect", "Prospect"),
                            ("former", "Former"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "billing_address",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "billing_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "payment_terms",
                    models.IntegerField(default=30, help_text="Payment terms in days"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["name"], name="core_client_name_76d9ae_idx"),
                    models.Index(fields=["email"], name="core_client_email_9bd669_idx"),
                    models.Index(
                        fields=["status"], name="core_client_status_d6704e_idx"
                    ),
                    models.Index(
                        fields=["created_at"], name="core_client_created_f91eae_idx"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, null=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=18)),
                (
                    "tax_amount",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=18),
                ),
                (
                    "category",
                    models.CharField(choices=CATEGORY_CHOICES, max_length=100),
                ),
                (
                    "tax_status",
                    models.CharField(
                        choices=[
                            ("taxable", "Taxable"),
                            ("non_taxable", "Non-Taxable"),
                        ],
                        default="taxable",
                        max_length=20,
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("cash", "Cash"),
                            ("credit_card", "Credit Card"),
                            ("debit_card", "Debit Card"),
                            ("bank_transfer", "Bank Transfer"),
                            ("cheque", "Cheque"),
                            ("paypal", "PayPal"),
                            ("other", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "payment_reference",
                    models.CharField(
                        blank=True,
                        help_text="Reference number, cheque number, or transaction ID",
                        max_length=100,
                        null=True,
                    ),
                ),
                ("date", models.DateField(help_text="Date of expense")),
                (
                    "due_date",
                    models.DateField(
                        blank=True,
                        help_text="Due date for payment if applicable",
                        null=True,
                    ),
                ),
                ("paid_date", models.DateField(blank=True, null=True)),
                ("is_recurring", models.BooleanField(default=False)),
                (
                    "recurring_frequency",
                    models.CharField(
                        choices=[
                            ("none", "Not Recurring"),
                            ("daily", "Daily"),
                            ("weekly", "Weekly"),
                            ("monthly", "Monthly"),
                            ("quarterly", "Quarterly"),
                            ("yearly", "Yearly"),
                        ],
                        default="none",
                        max_length=20,
                    ),
                ),
                ("recurring_end_date", models.DateField(blank=True, null=True)),
                (
                    "receipt",
                    models.FileField(
                        blank=True, null=True, upload_to="receipts/%Y/%m/"
                    ),
                ),
                (
                    "invoice_number",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("vendor", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "vendor_tax_number",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("paid", "Paid"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_expenses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submitted_expenses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "code",
                    models.CharField(
                        help_text="Unique project code/identifier",
                        max_length=20,
                        unique=True,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planning", "Planning"),
                            ("in_progress", "In Progress"),
                            ("on_hold", "On Hold"),
                            ("completed", "Completed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="planning",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("urgent", "Urgent"),
                        ],
                        default="medium",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("actual_start_date", models.DateField(blank=True, null=True)),
                ("actual_end_date", models.DateField(blank=True, null=True)),
                (
                    "budget",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=18,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "actual_cost",
                    models.DecimalField(decimal_places=2, default=0, max_digits=18),
                ),
                (
                    "hourly_rate",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "estimated_hours",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("github_repo", models.URLField(blank=True, null=True)),
                ("documentation_url", models.URLField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projects",
                        to="core.client",
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="managed_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "team_members",
                    models.ManyToManyField(
                        blank=True,
                        related_name="assigned_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "invoice_number",
                    models.CharField(editable=False, max_length=50, unique=True),
                ),
                ("date", models.DateField()),
                ("due_date", models.DateField()),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.00"))
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("sent", "Sent"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoices",
                        to="core.client",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invoices",
                        to="core.project",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="Income",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("date", models.DateField()),
                ("expected_date", models.DateField(blank=True, null=True)),
                ("received_date", models.DateField(blank=True, null=True)),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("cash", "Cash"),
                            ("cheque", "Cheque"),
                            ("bank_transfer", "Bank Transfer"),
                            ("credit_card", "Credit Card"),
                            ("paypal", "PayPal"),
                            ("other", "Other"),
                        ],
                        default="bank_transfer",
                        max_length=50,
                    ),
                ),
                (
                    "payment_reference",
                    models.CharField(
                        blank=True,
                        help_text="Transaction ID, cheque number, etc.",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("received", "Received"),
                            ("failed", "Failed"),
                            ("refunded", "Refunded"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "income_type",
                    models.CharField(
                        choices=[
                            ("project_payment", "Project Payment"),
                            ("retainer", "Retainer Fee"),
                            ("consultation", "Consultation"),
                            ("maintenance", "Maintenance"),
                            ("other", "Other"),
                        ],
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "tax_rate",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                (
                    "tax_amount",
                    models.DecimalField(decimal_places=2, default=0, max_digits=18),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incomes",
                        to="core.client",
                    ),
                ),
                (
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="incomes",
                        to="core.invoice",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incomes",
                        to="core.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Income",
                "verbose_name_plural": "Income",
                "ordering": ["-date", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("urgent", "Urgent"),
                        ],
                        default="medium",
                        max_length=20,
                    ),
                ),
                (
                    "task_type",
                    models.CharField(
                        choices=[
                            ("feature", "Feature"),
                            ("bug", "Bug"),
                            ("improvement", "Improvement"),
                            ("maintenance", "Maintenance"),
                            ("documentation", "Documentation"),
                            ("other", "Other"),
                        ],
                        default="feature",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("in_progress", "In Progress"),
                            ("review", "In Review"),
                            ("completed", "Completed"),
                            ("blocked", "Blocked"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=50,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("due_date", models.DateField()),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "estimated_hours",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "actual_hours",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("github_issue", models.URLField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                (
                    "tags",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated tags",
                        max_length=200,
                        null=True,
                    ),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "dependencies",
                    models.ManyToManyField(
                        blank=True, related_name="dependent_tasks", to="core.task"
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="core.project",
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewing_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-priority", "due_date"],
            },
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["role"], name="core_user_role_73872d_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["department"], name="core_user_departm_04962c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["status"], name="core_user_status_6589e6_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["employee_id"], name="core_user_employe_506d81_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["date"], name="core_expens_date_d957f6_idx"),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(
                fields=["category"], name="core_expens_categor_358de0_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(fields=["status"], name="core_expens_status_32e345_idx"),
        ),
        migrations.AddIndex(
            model_name="expense",
            index=models.Index(
                fields=["is_recurring"], name="core_expens_is_recu_9e3925_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["status"], name="core_projec_status_2020cc_idx"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(
                fields=["start_date"], name="core_projec_start_d_345e9e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(
                fields=["client"], name="core_projec_client__9c8c9d_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["code"], name="core_projec_code_119884_idx"),
        ),
        migrations.AddIndex(
            model_name="income",
            index=models.Index(fields=["date"], name="core_income_date_790cb6_idx"),
        ),
        migrations.AddIndex(
            model_name="income",
            index=models.Index(fields=["status"], name="core_income_status_f84b0b_idx"),
        ),
        migrations.AddIndex(
            model_name="income",
            index=models.Index(
                fields=["income_type"], name="core_income_income__06ca8a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(fields=["status"], name="core_task_status_e18e62_idx"),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["priority"], name="core_task_priorit_e802be_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["due_date"], name="core_task_due_dat_d0a0d3_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["assigned_to"], name="core_task_assigne_5f3995_idx"
            ),
        ),
    ]
