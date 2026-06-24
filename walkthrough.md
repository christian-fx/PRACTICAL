# Phase 1 Walkthrough — Project Scaffolding

## What We Built

A fully functional Django project skeleton with DRF integration, ready to receive our account management features in subsequent phases.

---

## File-by-File Breakdown

### 📦 [requirements.txt](file:///c:/Users/allwe/ANTI%20GRAVITY%20PROJECTS/PRACTICAL/requirements.txt)

```
django>=4.2,<5.0
djangorestframework>=3.14,<4.0
```

**Why these versions?**
- **Django 4.2** is the current **LTS** (Long Term Support) release — it gets security patches until April 2026. We pin `<5.0` to avoid accidentally pulling in Django 5.x which has breaking changes.
- **DRF 3.14+** is the stable release line that supports Django 4.2. We pin `<4.0` for the same forward-protection reason.
- We did **not** add `djangorestframework-simplejwt` because we're using Django's simpler built-in **Token Authentication** — one token per user, stored in the database. This is sufficient for this API and avoids extra complexity.

---

### 🏗️ Project Structure

```
PRACTICAL/
├── manage.py              ← Django CLI entry point
├── requirements.txt       ← Dependencies
├── core/                  ← Django project config
│   ├── __init__.py
│   ├── settings.py        ← All configuration
│   ├── urls.py            ← Root URL router
│   └── wsgi.py            ← WSGI entry point
└── accounts/              ← Our custom app
    ├── __init__.py
    ├── apps.py            ← App config
    ├── admin.py           ← Admin registrations (Phase 2)
    ├── models.py          ← Models (Phase 2)
    ├── serializers.py     ← Serializers (Phase 3)
    ├── views.py           ← Views (Phase 3)
    ├── urls.py            ← URL routes (Phase 3)
    └── tests.py           ← Tests (Phase 4)
```

**Why this layout?**
- `core/` holds project-level config (settings, root URLs, WSGI). This is the standard Django convention — the project package is separate from app packages.
- `accounts/` is a dedicated Django app for account management. Django encourages splitting functionality into apps for modularity and reusability. All deactivation/reactivation logic lives here.

---

### ⚙️ [core/settings.py](file:///c:/Users/allwe/ANTI%20GRAVITY%20PROJECTS/PRACTICAL/core/settings.py)

Key decisions explained:

#### Security Settings (Lines 18–25)

```python
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-me-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
```

- All sensitive values are **environment-variable driven** with dev-safe defaults. This means:
  - In development: works out of the box with no `.env` file
  - In production: you set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DJANGO_ALLOWED_HOSTS=yourdomain.com`
- The `django-insecure-` prefix is a Django convention that triggers a security warning if you accidentally deploy with it.

#### Installed Apps (Lines 30–43)

```python
INSTALLED_APPS = [
    # Django built-ins ...
    "rest_framework",
    "rest_framework.authtoken",   # Token-based auth
    "accounts",
]
```

- `rest_framework` — Enables DRF (serializers, views, authentication, permissions)
- `rest_framework.authtoken` — Creates the `authtoken_token` database table that stores one token per user. This is what powers our `Token` authentication.
- `accounts` — Our custom app (registered so Django discovers its models, migrations, and admin config)

#### DRF Configuration (Lines 115–124)

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

- **TokenAuthentication** is set as the **global default** — every DRF view requires a valid `Authorization: Token <key>` header unless explicitly overridden.
- **IsAuthenticated** is the **global default permission** — anonymous requests are rejected with `401 Unauthorized`.
- This means our deactivate/reactivate endpoints get auth protection "for free" without decorating each view.

#### Database (Lines 87–93)

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

- SQLite for development — zero config, file-based, perfect for local dev and testing.
- Swap to PostgreSQL in production by changing `ENGINE` and adding connection details.

---

### 🔀 [core/urls.py](file:///c:/Users/allwe/ANTI%20GRAVITY%20PROJECTS/PRACTICAL/core/urls.py)

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("accounts.urls")),
    path("api-token-auth/", obtain_auth_token, name="api-token-auth"),
]
```

Three routes:

| URL | Purpose |
|---|---|
| `/admin/` | Django admin panel for managing users, viewing audit logs |
| `/account/` | All our account endpoints (deactivate, reactivate) — delegated to `accounts/urls.py` |
| `/api-token-auth/` | **Built-in DRF view** — POST `username` + `password`, get back a token. We need this so users can authenticate before calling our endpoints |

**Why `/api-token-auth/`?** — Without it, there's no way to obtain a token. This is DRF's out-of-the-box solution. You POST credentials, it returns `{"token": "abc123..."}`, and you use that token in the `Authorization` header for all subsequent requests.

---

### 📱 [accounts/apps.py](file:///c:/Users/allwe/ANTI%20GRAVITY%20PROJECTS/PRACTICAL/accounts/apps.py)

```python
class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Account Management"
```

- `BigAutoField` — Uses 64-bit integers for primary keys (Django 3.2+ default). Future-proofs against integer overflow on high-volume tables.
- `verbose_name` — Shows "Account Management" in the Django admin sidebar instead of the generic "Accounts".

---

## Verification

```
$ python manage.py check
System check identified no issues (0 silenced).
```

✅ Django found all apps, resolved all URL patterns, validated all settings — **zero errors, zero warnings**.

---

## What's Next — Phase 2

In Phase 2, we'll build the **data layer**:
1. `AccountState` model — tracks whether an account is active/inactive with timestamps
2. `AuditLog` model — immutable append-only record of every state change
3. Run migrations to create the database tables
4. Register both models in Django admin

Ready to proceed when you are!
