from rest_framework import serializers
from .models import AccountState

class DeactivateSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, min_length=10, max_length=500)

class ReactivateSerializer(serializers.Serializer):
    # No extra fields required for reactivation based on requirements
    pass

class AccountStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountState
        fields = ['is_active', 'deactivated_at', 'reactivated_at', 'deactivation_reason']

