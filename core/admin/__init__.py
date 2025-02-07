from django.contrib import admin

from core.models import Task

from .client import ClientAdmin
from .finance.expense import ExpenseAdmin
from .finance.income import IncomeAdmin
from .finance.invoice import InvoiceAdmin
from .project import ProjectAdmin
from .task import TaskAdmin
# Import admin classes
from .user import UserAdmin

# Customize Admin Header
admin.site.site_header = "TitansManager Admin"
admin.site.site_title = "TitansManager Admin Portal"
admin.site.index_title = "Welcome to TitansManager Admin"
