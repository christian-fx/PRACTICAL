# Phase 5 Walkthrough — Verification & Beginner's Testing Guide

## What We Did
In Phase 5, we ran the final round of verification to prove that everything we built in Phases 1–4 works end-to-end. This includes:
- ✅ **Automated tests** — 9/9 passed
- ✅ **Manual test: No auth** — Correctly rejected with 401
- ✅ **Manual test: Deactivation** — Returns 200, sets `is_active=False`, stores reason
- ✅ **Manual test: Reactivation** — Returns 200, sets `is_active=True`, clears reason
- ✅ **Audit log verification** — 2 entries (DEACTIVATE + REACTIVATE) with correct data

---

## 🧑‍🎓 Beginner's Step-by-Step Guide: How to Run Everything

### Prerequisites

Before you start, make sure you have:
1. **Python 3.10+** installed (check with `python --version`)
2. A **terminal** open (PowerShell on Windows, Terminal on Mac/Linux)
3. Navigate to the project folder:

```
cd "c:\Users\allwe\ANTI GRAVITY PROJECTS\PRACTICAL"
```

> [!TIP]
> All commands below should be run from **inside this project folder**. Never change directories after this step.

---

### Step 1 — Install Dependencies (One-Time Setup)

This installs Django and Django REST Framework:

```bash
pip install -r requirements.txt
```

**What this does:** Reads the `requirements.txt` file and downloads/installs the two libraries we need:
- `django` — The web framework
- `djangorestframework` — The API toolkit that sits on top of Django

**Expected output:** You should see lines ending with `Successfully installed django-4.2.x djangorestframework-3.x.x`

---

### Step 2 — Create Database Tables (One-Time Setup)

```bash
python manage.py migrate
```

**What this does:** Creates all the database tables (for users, tokens, account states, audit logs, etc.) inside a local `db.sqlite3` file. Think of it as "setting up the spreadsheet columns" before you can start saving data.

**Expected output:** A list of `Applying ... OK` lines.

---

### Step 3 — Run Automated Tests

This is the most important verification step. One command runs all 9 tests:

```bash
python manage.py test accounts -v 2
```

**Breaking down the command:**
| Part | Meaning |
|---|---|
| `python manage.py` | Run Django's management tool |
| `test` | Run the test suite |
| `accounts` | Only run tests in the `accounts` app |
| `-v 2` | Verbose level 2 — show each test name and result |

**Expected output:**
```
test_audit_log_entries ... ok
test_deactivate_already_inactive ... ok
test_deactivate_reason_min_length ... ok
test_deactivate_requires_auth ... ok
test_deactivate_requires_reason ... ok
test_deactivate_success ... ok
test_reactivate_already_active ... ok
test_reactivate_requires_auth ... ok
test_reactivate_success ... ok

----------------------------------------------------------------------
Ran 9 tests in ~13s

OK
```

> [!IMPORTANT]
> If you see `FAILED` instead of `OK`, something is wrong. Read the error message — it will tell you exactly which test failed and why.

**What each test checks:**

| # | Test Name | What It Verifies |
|---|---|---|
| 1 | `test_deactivate_requires_auth` | Can't deactivate without a token → 401 |
| 2 | `test_deactivate_requires_reason` | Can't deactivate without a reason → 400 |
| 3 | `test_deactivate_reason_min_length` | Reason must be ≥10 characters → 400 |
| 4 | `test_deactivate_success` | Valid deactivation → 200, user inactive, audit logged |
| 5 | `test_deactivate_already_inactive` | Can't deactivate twice → 401 (blocked by auth) |
| 6 | `test_reactivate_requires_auth` | Can't reactivate without a token → 401 |
| 7 | `test_reactivate_already_active` | Can't reactivate an active account → 400 |
| 8 | `test_reactivate_success` | Valid reactivation → 200, user active, audit logged |
| 9 | `test_audit_log_entries` | Full cycle produces exactly 2 ordered audit entries |

---

### Step 4 — Manual Testing with the Dev Server

If you want to test the API yourself (like using Postman or curl), follow these steps:

#### 4a. Create a Test User

```bash
python manage.py createsuperuser
```

It will ask you for:
- **Username:** (e.g., `testuser`)
- **Email:** (e.g., `test@example.com`)
- **Password:** (e.g., `mypassword123`)

#### 4b. Start the Development Server

```bash
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

> [!NOTE]
> The server runs **in the foreground** — it will keep running until you press `Ctrl+C`. Open a **second terminal** for the next steps.

#### 4c. Get an Authentication Token

In your **second terminal**, run:

```bash
python -c "from urllib.request import Request, urlopen; import json; data = json.dumps({'username': 'testuser', 'password': 'mypassword123'}).encode(); req = Request('http://127.0.0.1:8000/api-token-auth/', data=data, headers={'Content-Type': 'application/json'}, method='POST'); resp = urlopen(req); print(json.loads(resp.read()))"
```

**Expected output:**
```
{'token': 'abc123def456...'}
```

📋 **Copy that token value** — you'll need it for the next steps. Replace `YOUR_TOKEN` below with it.

#### 4d. Test Deactivation

```bash
python -c "from urllib.request import Request, urlopen; import json; data = json.dumps({'reason': 'I need a break from the platform for personal reasons.'}).encode(); req = Request('http://127.0.0.1:8000/account/deactivate/', data=data, headers={'Authorization': 'Token YOUR_TOKEN', 'Content-Type': 'application/json'}, method='POST'); resp = urlopen(req); print(f'Status: {resp.status}'); print(json.loads(resp.read()))"
```

**Expected output:**
```
Status: 200
{'is_active': False, 'deactivated_at': '2026-...', 'reactivated_at': None, 'deactivation_reason': 'I need a break from the platform for personal reasons.'}
```

#### 4e. Test Reactivation

```bash
python -c "from urllib.request import Request, urlopen; import json; data = json.dumps({}).encode(); req = Request('http://127.0.0.1:8000/account/reactivate/', data=data, headers={'Authorization': 'Token YOUR_TOKEN', 'Content-Type': 'application/json'}, method='POST'); resp = urlopen(req); print(f'Status: {resp.status}'); print(json.loads(resp.read()))"
```

**Expected output:**
```
Status: 200
{'is_active': True, 'deactivated_at': '2026-...', 'reactivated_at': '2026-...', 'deactivation_reason': ''}
```

#### 4f. Verify Audit Logs

```bash
python manage.py shell -c "from accounts.models import AuditLog; logs = AuditLog.objects.all().order_by('performed_at'); print(f'Total audit entries: {logs.count()}'); [print(f'  [{l.action}] user={l.user.username} reason={repr(l.reason)} at={l.performed_at}') for l in logs]"
```

**Expected output:**
```
Total audit entries: 2
  [DEACTIVATE] user=testuser reason='I need a break...' at=2026-...
  [REACTIVATE] user=testuser reason='' at=2026-...
```

#### 4g. View in Django Admin (Optional)

1. Open your browser and go to: **http://127.0.0.1:8000/admin/**
2. Log in with the superuser credentials you created
3. Click **"Account States"** to see user statuses
4. Click **"Audit logs"** to see the immutable audit trail

> [!NOTE]
> Audit logs in the admin are **read-only** — you cannot add, edit, or delete them. This is by design for data integrity.

---

## 📊 Verification Results Summary

| Test | Method | Result |
|---|---|---|
| 9 automated unit tests | `python manage.py test accounts -v 2` | ✅ All passed |
| Unauthenticated request blocked | Manual POST without token | ✅ 401 returned |
| Deactivation with valid token + reason | Manual POST to `/account/deactivate/` | ✅ 200, `is_active=False` |
| Reactivation with valid token | Manual POST to `/account/reactivate/` | ✅ 200, `is_active=True` |
| Audit log integrity | Django shell query | ✅ 2 entries, correct data |

---

## 🏁 Project Complete!

All 5 phases are done. Here's the final file structure:

```
PRACTICAL/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── core/
│   ├── __init__.py
│   ├── settings.py       ← DRF + Token Auth configured
│   ├── urls.py            ← Root routes (admin, account, token-auth)
│   └── wsgi.py
└── accounts/
    ├── __init__.py
    ├── apps.py
    ├── admin.py           ← Read-only audit log admin
    ├── models.py          ← AccountState + AuditLog
    ├── serializers.py     ← Input validation + response formatting
    ├── views.py           ← Deactivate/Reactivate logic + custom auth
    ├── urls.py            ← /account/deactivate/ + /account/reactivate/
    ├── tests.py           ← 9 test cases
    └── migrations/
        └── 0001_initial.py
```

### API Endpoints

| Endpoint | Method | Auth | Body | Response |
|---|---|---|---|---|
| `/api-token-auth/` | POST | None | `{"username": "...", "password": "..."}` | `{"token": "..."}` |
| `/account/deactivate/` | POST | Token | `{"reason": "..."}` (10-500 chars) | `AccountState` object |
| `/account/reactivate/` | POST | Token | `{}` (empty) | `AccountState` object |
