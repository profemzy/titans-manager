from django.db import models
from .mixins.timestamp import TimestampMixin


class Client(TimestampMixin):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("prospect", "Prospect"),
        ("former", "Former"),
    ]

    # Basic Information
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)

    # Contact Information
    alternate_email = models.EmailField(blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Address Information
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    # Business Information
    tax_number = models.CharField(
        max_length=50, blank=True, null=True, help_text="VAT/GST/Tax ID"
    )
    industry = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True, null=True)

    # Billing Information
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    billing_email = models.EmailField(blank=True, null=True)
    payment_terms = models.IntegerField(default=30, help_text="Payment terms in days")

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        if self.company:
            return f"{self.name} ({self.company})"
        return self.name

    def get_full_address(self):
        """Returns formatted full address."""
        parts = [self.address, self.city, self.state, self.postal_code, self.country]
        return ", ".join(filter(None, parts))

    @property
    def total_projects(self):
        """Returns total number of projects."""
        return self.projects.count()

    @property
    def total_revenue(self):
        """Returns total revenue from client."""
        return self.incomes.aggregate(total=models.Sum("amount"))["total"] or 0

    @property
    def outstanding_invoices(self):
        """Returns queryset of unpaid invoices."""
        return self.invoices.filter(status="Unpaid")

    @property
    def total_outstanding(self):
        """Returns total amount of unpaid invoices."""
        return (
            self.outstanding_invoices.aggregate(total=models.Sum("amount"))["total"]
            or 0
        )
