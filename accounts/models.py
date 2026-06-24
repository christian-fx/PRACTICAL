from django.db import models
from django.contrib.auth.models import User

class AccountState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_state')
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    reactivated_at = models.DateTimeField(null=True, blank=True)
    deactivation_reason = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.user.username} State - Active: {self.is_active}"

class AuditLog(models.Model):
    class Action(models.TextChoices):
        DEACTIVATE = 'DEACTIVATE', 'Deactivate'
        REACTIVATE = 'REACTIVATE', 'Reactivate'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    reason = models.TextField(blank=True, default='')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_audits')
    performed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # extensible extra data

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.performed_at}"

