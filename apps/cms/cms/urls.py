"""
URL configuration for CMS project.

Includes:
- Admin interface
- JWT token endpoints (via simplejwt)
- Health check
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


def health_check(request):
    """Health check endpoint."""
    return JsonResponse({"status": "ok", "service": "cms"})


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # JWT endpoints (used by FastAPI to verify tokens)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Health
    path('health/', health_check, name='health'),
]
