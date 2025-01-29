import datetime

from django.contrib import admin
from .models import User, Client, Project, Task, Income, Expense, Invoice
from rangefilter.filters import DateRangeFilter
from django.utils.html import format_html
from django.db.models import Sum

# Customize Admin Header
admin.site.site_header = "TitansManager Admin"
admin.site.site_title = "TitansManager Admin Portal"
admin.site.index_title = "Welcome to TitansManager Admin"

# Inline for Tasks
class TaskInline(admin.TabularInline):
    model = Task
    extra = 1

# Register Models
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    search_fields = ('username', 'email')
    list_filter = ('role',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company')
    search_fields = ('name', 'email', 'company')
    list_filter = ('company',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'start_date', 'end_date', 'budget')
    search_fields = ('name', 'client__name')
    list_filter = ('client', 'start_date', 'end_date')
    inlines = [TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'assigned_to', 'status', 'due_date')
    search_fields = ('name', 'project__name', 'assigned_to__username')
    list_filter = ('status', 'project', 'assigned_to')


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('display_amount', 'client', 'project', 'income_type',
                    'date', 'status', 'payment_method', 'display_overdue')

    list_filter = (
        'status',
        'income_type',
        'payment_method',
        ('date', DateRangeFilter),
        'client',
        'project'
    )

    search_fields = (
        'client__name',
        'project__name',
        'payment_reference',
        'description'
    )

    readonly_fields = ('created_at', 'updated_at', 'tax_amount', 'total_amount')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'client', 'project', 'income_type', 'amount', 'description'
            )
        }),
        ('Dates', {
            'fields': (
                'date', 'expected_date', 'received_date'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method', 'payment_reference', 'status', 'invoice'
            )
        }),
        ('Tax Information', {
            'fields': (
                'tax_rate', 'tax_amount'
            )
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def display_amount(self, obj):
        return f"${obj.amount:,.2f}"

    display_amount.short_description = 'Amount'
    display_amount.admin_order_field = 'amount'

    def display_overdue(self, obj):
        if obj.is_overdue:
            return f"⚠️ {obj.days_overdue} days"
        return "✓"

    display_overdue.short_description = 'Overdue'

    actions = ['mark_as_received', 'mark_as_pending']

    def mark_as_received(self, request, queryset):
        queryset.update(
            status='received',
            received_date=datetime.date.today()
        )

    mark_as_received.short_description = "Mark selected incomes as received"

    def mark_as_pending(self, request, queryset):
        queryset.update(
            status='pending',
            received_date=None
        )

    mark_as_pending.short_description = "Mark selected incomes as pending"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_income': queryset.aggregate(
                total=Sum('amount'))['total'] or 0,
            'pending_income': queryset.filter(
                status='pending').aggregate(
                total=Sum('amount'))['total'] or 0,
            'received_income': queryset.filter(
                status='received').aggregate(
                total=Sum('amount'))['total'] or 0
        }

        response.context_data['summary_metrics'] = metrics
        return response


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'display_total', 'date',
                    'status', 'is_recurring', 'receipt_link')
    list_filter = (
        'status',
        'category',
        'payment_method',
        'is_recurring',
        ('date', DateRangeFilter),
        'tax_status',
    )
    search_fields = ('title', 'description', 'vendor', 'invoice_number')
    readonly_fields = ('created_at', 'updated_at', 'total_amount')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'amount', 'tax_amount', 'category')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_reference', 'tax_status',
                       'date', 'due_date', 'paid_date')
        }),
        ('Recurring Settings', {
            'fields': ('is_recurring', 'recurring_frequency', 'recurring_end_date'),
            'classes': ('collapse',)
        }),
        ('Documentation', {
            'fields': ('receipt', 'invoice_number', 'vendor', 'vendor_tax_number')
        }),
        ('Approval Information', {
            'fields': ('status', 'submitted_by', 'approved_by', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_total(self, obj):
        return f"${obj.total_amount:.2f}"

    display_total.short_description = 'Total Amount'

    def receipt_link(self, obj):
        if obj.receipt:
            return format_html('<a href="{}" target="_blank">View Receipt</a>',
                               obj.receipt.url)
        return "No receipt"

    receipt_link.short_description = 'Receipt'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('submitted_by', 'approved_by')

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new expense
            obj.submitted_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['mark_as_approved', 'mark_as_paid']

    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved', approved_by=request.user)

    mark_as_approved.short_description = "Mark selected expenses as approved"

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid', paid_date=datetime.date.today())

    mark_as_paid.short_description = "Mark selected expenses as paid"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_amount': queryset.aggregate(
                total=Sum('amount') + Sum('tax_amount'))['total'] or 0,
            'pending_amount': queryset.filter(
                status='pending').aggregate(
                total=Sum('amount') + Sum('tax_amount'))['total'] or 0,
        }

        response.context_data['summary_metrics'] = metrics
        return response

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('client', 'project', 'amount', 'date', 'status')
    search_fields = ('client__name', 'project__name')
    list_filter = ('status', 'date', 'client')
