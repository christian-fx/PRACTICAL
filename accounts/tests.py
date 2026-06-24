from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import AccountState, AuditLog

class AccountStateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.deactivate_url = reverse('account-deactivate')
        self.reactivate_url = reverse('account-reactivate')

    def test_deactivate_requires_auth(self):
        """Test that deactivation fails without auth."""
        response = self.client.post(self.deactivate_url, {'reason': 'Leaving for a while.'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivate_requires_reason(self):
        """Test that deactivation requires a reason field."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.deactivate_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reason', response.data)

    def test_deactivate_reason_min_length(self):
        """Test that reason must be at least 10 characters."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.deactivate_url, {'reason': 'Short'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deactivate_success(self):
        """Test successful account deactivation."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.deactivate_url, {'reason': 'I need a break from this app.'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify User model
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        # Verify AccountState
        state = AccountState.objects.get(user=self.user)
        self.assertFalse(state.is_active)
        self.assertEqual(state.deactivation_reason, 'I need a break from this app.')
        self.assertIsNotNone(state.deactivated_at)
        
        # Verify Audit Log
        audit = AuditLog.objects.get(user=self.user)
        self.assertEqual(audit.action, AuditLog.Action.DEACTIVATE)
        self.assertEqual(audit.reason, 'I need a break from this app.')
        self.assertEqual(audit.performed_by, self.user)

    def test_deactivate_already_inactive(self):
        """Test deactivating an already deactivated account fails."""
        self.test_deactivate_success() # Deactivate it first
        
        # Try again
        response = self.client.post(self.deactivate_url, {'reason': 'Another reason.'})
        # Since the user was deactivated (is_active=False), TokenAuthentication will reject them 
        # as unauthorized before the view logic even runs.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reactivate_requires_auth(self):
        """Test that reactivation fails without auth."""
        response = self.client.post(self.reactivate_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reactivate_already_active(self):
        """Test that reactivating an active account fails."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.reactivate_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Account is already active.')

    def test_reactivate_success(self):
        """Test successful reactivation of a deactivated account."""
        # Deactivate first
        self.test_deactivate_success()
        
        # Ensure user is actually inactive
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        # Reactivate using the same token
        response = self.client.post(self.reactivate_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify User model
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        
        # Verify AccountState
        state = AccountState.objects.get(user=self.user)
        self.assertTrue(state.is_active)
        self.assertEqual(state.deactivation_reason, '')
        self.assertIsNotNone(state.reactivated_at)
        
        # Verify Audit Log (should have 2 entries now)
        self.assertEqual(AuditLog.objects.filter(user=self.user).count(), 2)
        latest_audit = AuditLog.objects.filter(user=self.user).order_by('-performed_at').first()
        self.assertEqual(latest_audit.action, AuditLog.Action.REACTIVATE)
        self.assertEqual(latest_audit.performed_by, self.user)

    def test_audit_log_entries(self):
        """Verify the total integrity of the audit trail after full cycle."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client.post(self.deactivate_url, {'reason': 'Temp leave'})
        self.client.post(self.reactivate_url, {})
        
        logs = AuditLog.objects.filter(user=self.user).order_by('performed_at')
        self.assertEqual(logs.count(), 2)
        self.assertEqual(logs[0].action, AuditLog.Action.DEACTIVATE)
        self.assertEqual(logs[0].reason, 'Temp leave')
        self.assertEqual(logs[1].action, AuditLog.Action.REACTIVATE)
        self.assertEqual(logs[1].reason, '')

