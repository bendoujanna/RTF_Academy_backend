# CI/CD & Deployment Architecture

This repository is configured with an automated Continuous Integration (CI) pipeline and a decoupled cloud deployment architecture to ensure code reliability, security, and high performance.

```
[ GitHub Repo ] ───( Push / PR )───► [ GitHub Actions (CI) ]
       │                                     │ (Runs Tests)
       ▼ (Auto-Deploy)                       ▼
 [ Render Web Service ] ◄──────────────── [ Neon Postgres DB ]
       │
 [ Firebase Admin SDK ] (Production Auth)
```

---

## 1. Continuous Integration (GitHub Actions)

The workflow file lives at `.github/workflows/django-ci.yml`. It triggers automatically on every push or pull request to the `main` branch.

**Environment:** Ubuntu Linux running Python 3.12 to fully support Django 6.0.6+.

**Automation Steps:**

1. Installs all project dependencies from `requirements.txt`.
2. Runs Django system checks and runs the automated test suite (`python manage.py test`).

**CI Safety Guard:** The application initialization block gracefully catches missing production secrets (like the Firebase credentials file) inside the CI environment, allowing the test suite to run natively without mocking complex authenticators.

---

## 2. Database Architecture (Neon.tech)

The project utilizes a cloud-hosted, serverless PostgreSQL database provided by Neon.tech.

- **Connection Protocol:** Connections are parsed dynamically via `dj-database-url`.
- **Connection Pooling:** In production, the app utilizes Neon's pooled connection configuration string. It includes `conn_max_age=600` and `conn_health_checks=True` in `settings.py` to maintain persistent database connections, eliminating the overhead of re-opening connections on every API request.

---

## 3. Production Deployment (Render)

The Django application is hosted as a Web Service on Render.

- **Runtime:** Native Python 3 environment.
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python manage.py migrate
  ```
- **Start Command:**
  ```bash
  gunicorn core.wsgi:application
  ```
  Uses Gunicorn to handle concurrent production traffic instead of the local development server.
- **Security (`ALLOWED_HOSTS`):** Hardcoded to trust explicitly defined origins (`localhost`, `127.0.0.1`, and `rtf-academy-backend.onrender.com`) to neutralize HTTP Host Header manipulation exploits.

---

## 4. Environment Variables & Production Secrets

Production variables are managed securely within the Render Environment Dashboard and are never exposed in source control.

| Variable Name | Purpose | Example Value |
|---|---|---|
| `DATABASE_URL` | Neon PostgreSQL pooled connection string | `postgres://user:pass@ep-pool-123.neon.tech/db?sslmode=require` |
| `SECRET_KEY` | Django's cryptographic signing key | `django-insecure-xxx...` |
| `PYTHON_VERSION` | Forces the target server execution runtime | `3.12.0` |
| `FIREBASE_CREDENTIALS_PATH` | Points to the securely injected JSON file | `firebase-credentials.json` |

### Firebase Admin Integration

Because the Firebase service account key contains sensitive private keys, it is uploaded directly to Render via Secret Files as `firebase-credentials.json`. The environment variable `FIREBASE_CREDENTIALS_PATH` maps directly to this file, enabling live verification of incoming client authentication tokens using the Firebase Admin SDK.