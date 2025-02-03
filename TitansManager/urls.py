from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin
from core.views import HealthCheckView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing_page.html'), name='home'),
    path('titans-admin/', admin.site.urls),

    path('auth/', include('django.contrib.auth.urls')),
    path('api/', include('core.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/health/', HealthCheckView.as_view(), name=''),
]
