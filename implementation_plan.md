# Account Deactivate/Reactivate API Endpoints

Build Django REST Framework API endpoints for account deactivation and reactivation with full audit trail and account state management.

## Requirements Summary

| Requirement | Detail |
|---|---|
| **Endpoints** | `POST /account/deactivate/` · `POST /account/reactivate/` |
| **Auth** | Token-based authentication required on both |
| **Validation** | `reason` field required on deactivation |
| **State Tracking** | Persist account `is_active` state on the User model |
| **Audit Trail** | Log every state change with actor, action, reason, timestamp |
| **Tests** | Full endpoint + model test coverage |

---

## Proposed Changes

### Phase 1 — Project Scaffolding

#### [NEW] Django project & `accounts` app

We'll initialize a Django project (`core`) and a dedicated `accounts` app:

```
PRACTICAL/
├── manage.py
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── accounts/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── permissions.py
    └── tests.py
```

**Dependencies:** `django`, `djangorestframework`

---

### Phase 2 — Models & Migrations

#### [NEW] `accounts/models.py`

Two models:

1. **`AccountState`** — Tracks the current deactivation state of a user account.

```python
class AccountState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_state')
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    reactivated_at = models.DateTimeField(null=True, blank=True)
    deactivation_reason = models.TextField(blank=True, default='')
```

2. **`AuditLog`** — Immutable append-only log of every account state change.

```python
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
```

> [!IMPORTANT]
> We use Django's built-in `User.is_active` field alongside our `AccountState` model. `AccountState` provides richer metadata, while `User.is_active` is kept in sync to leverage Django's built-in auth checks (inactive users are denied login automatically).

---

### Phase 3 — Serializers, Views & URLs

#### [NEW] `accounts/serializers.py`

```python
class DeactivateSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, min_length=10, max_length=500)

class ReactivateSerializer(serializers.Serializer):
    pass  # No extra fields required; auth is sufficient

class AccountStateSerializer(serializers.ModelSerializer):
    # Read-only serializer for response payloads
    class Meta:
        model = AccountState
        fields = ['is_active', 'deactivated_at', 'reactivated_at', 'deactivation_reason']
```

#### [NEW] `accounts/views.py`

Two `APIView` classes:

| View | Method | Logic |
|---|---|---|
| `DeactivateAccountView` | POST | Validate reason → set `is_active=False` → update `AccountState` → create `AuditLog` → return state |
| `ReactivateAccountView` | POST | Check already active → set `is_active=True` → update `AccountState` → create `AuditLog` → return state |

Both views:
- Require `IsAuthenticated` permission
- Use `transaction.atomic()` to ensure data consistency
- Return `200` on success with the current `AccountState`
- Return `400` for invalid transitions (e.g., deactivating an already inactive account)

#### [NEW] `accounts/urls.py`

```python
urlpatterns = [
    path('deactivate/', DeactivateAccountView.as_view(), name='account-deactivate'),
    path('reactivate/', ReactivateAccountView.as_view(), name='account-reactivate'),
]
```

#### [MODIFY] `core/urls.py`

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
]
```

---

### Phase 4 — Tests

#### [NEW] `accounts/tests.py`

| Test Case | Description |
|---|---|
| `test_deactivate_requires_auth` | Unauthenticated → 401 |
| `test_deactivate_requires_reason` | Missing reason → 400 |
| `test_deactivate_success` | Valid request → 200, user becomes inactive, audit log created |
| `test_deactivate_already_inactive` | Already inactive → 400 |
| `test_reactivate_requires_auth` | Unauthenticated → 401 |
| `test_reactivate_success` | Valid request → 200, user becomes active, audit log created |
| `test_reactivate_already_active` | Already active → 400 |
| `test_audit_log_entries` | Both actions produce correct audit entries |

---

## Open Questions

> [!IMPORTANT]
> **Authentication method:** Should we use Django REST Framework's **Token Authentication** (simple, built-in) or **JWT** (via `djangorestframework-simplejwt`)? I'll default to **Token Auth** for simplicity unless you prefer JWT.

> [!NOTE]
> **Self-service only or admin capability?** Currently planned as self-service (users deactivate/reactivate their own accounts). Should admins be able to deactivate/reactivate *other* users' accounts via the same endpoints? This can be added later as an enhancement.

> [!NOTE]
> **Reason on reactivation?** Currently `reason` is only required on deactivation per your spec. Should reactivation also accept an optional reason field for audit purposes?

---

## Verification Plan

### Automated Tests
```bash
python manage.py test accounts -v 2
```

### Manual Verification
1. Start dev server → `python manage.py runserver`
2. Create a user and obtain an auth token
3. Test deactivation via `curl` / Postman with and without reason
4. Test reactivation via `curl` / Postman
5. Verify audit log entries in Django admin
