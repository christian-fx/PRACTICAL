"""
core URL Configuration

Root URL router. Includes:
- /admin/          → Django admin
- /account/        → Account deactivate/reactivate endpoints
- /api-token-auth/ → Obtain auth token (POST username + password)
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("accounts.urls")),
    path("api-token-auth/", obtain_auth_token, name="api-token-auth"),
]
