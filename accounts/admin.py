from django.contrib import admin
from .models import AccountState, AuditLog

@admin.register(AccountState)
class AccountStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'deactivated_at', 'reactivated_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__email')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'performed_by', 'performed_at', 'ip_address')
    list_filter = ('action', 'performed_at')
    search_fields = ('user__username', 'performed_by__username', 'reason')
    # Audit logs should be immutable
    readonly_fields = ('user', 'action', 'reason', 'performed_by', 'performed_at', 'ip_address', 'metadata')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

