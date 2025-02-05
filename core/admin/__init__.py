from django.contrib import admin

from core.models import Task

# Customize Admin Header
admin.site.site_header = "TitansManager Admin"
admin.site.site_title = "TitansManager Admin Portal"
admin.site.index_title = "Welcome to TitansManager Admin"

# Import and register admin classes
from .user import UserAdmin
from .client import ClientAdmin
from .project import ProjectAdmin
from .task import TaskAdmin

from .finance.income import IncomeAdmin
from .finance.expense import ExpenseAdmin
from .finance.invoice import InvoiceAdmin

