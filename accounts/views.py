from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from .models import AccountState, AuditLog
from .serializers import DeactivateSerializer, ReactivateSerializer, AccountStateSerializer

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

class InactiveUserTokenAuthentication(TokenAuthentication):
    """Custom Token Auth that allows inactive users, so they can reactivate themselves."""
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')
        return (token.user, token)

class DeactivateAccountView(APIView):
    def post(self, request):
        serializer = DeactivateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        reason = serializer.validated_data['reason']
        
        with transaction.atomic():
            state, _ = AccountState.objects.get_or_create(user=request.user)
            
            if not state.is_active:
                return Response(
                    {"detail": "Account is already deactivated."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update AccountState
            state.is_active = False
            state.deactivated_at = timezone.now()
            state.deactivation_reason = reason
            state.save()
            
            # Sync User.is_active
            request.user.is_active = False
            request.user.save()
            
            # Log Audit
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.DEACTIVATE,
                reason=reason,
                performed_by=request.user,
                ip_address=self.get_client_ip(request)
            )
            
        return Response(AccountStateSerializer(state).data, status=status.HTTP_200_OK)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class ReactivateAccountView(APIView):
    # Override authentication to allow inactive users to hit this endpoint
    authentication_classes = [InactiveUserTokenAuthentication]
    
    def post(self, request):
        serializer = ReactivateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            state, _ = AccountState.objects.get_or_create(user=request.user)
            
            if state.is_active:
                return Response(
                    {"detail": "Account is already active."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update AccountState
            state.is_active = True
            state.reactivated_at = timezone.now()
            state.deactivation_reason = ''
            state.save()
            
            # Sync User.is_active
            request.user.is_active = True
            request.user.save()
            
            # Log Audit
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.REACTIVATE,
                performed_by=request.user,
                ip_address=self.get_client_ip(request)
            )
            
        return Response(AccountStateSerializer(state).data, status=status.HTTP_200_OK)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

