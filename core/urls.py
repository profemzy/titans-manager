from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ClientViewSet, ExpenseViewSet, IncomeViewSet,
                    InvoiceViewSet, ProjectViewSet, TaskViewSet, UserViewSet)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"incomes", IncomeViewSet)
router.register(r"expenses", ExpenseViewSet)
router.register(r"invoices", InvoiceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
