"""
Account URL routes.

Endpoints will be added in Phase 3.
"""

from django.urls import path
from .views import DeactivateAccountView, ReactivateAccountView

urlpatterns = [
    path('deactivate/', DeactivateAccountView.as_view(), name='account-deactivate'),
    path('reactivate/', ReactivateAccountView.as_view(), name='account-reactivate'),
]

