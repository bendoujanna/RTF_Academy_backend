# RTF Academy — Backend API

Django REST API powering the RTF Academy e-learning platform. Handles course delivery, learner progress tracking, quiz assessments, and certificate generation for the Raise Them Foundation.

---

## Tech Stack

- **Framework:** Django + Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** Firebase Auth (stateless, token-based)
- **Storage:** AWS S3 (course media and certificate PDFs)
- **Language:** Python 3.11+

---

## Project Structure

```
rtf-academy-backend/
├── core/                        # Project configuration
│
├── users/                       # Identity domain
│
├── courses/                     # Content domain
│
├── quizzes/                     # Assessment domain
│
├── progress/                    # Progress domain
│
├── certificates/                # Certificate domain
│   
├── manage.py
├── requirements.txt
└── .env
```

---

## Prerequisites

Make sure the following are installed on your machine before starting:

- Python 3.11+
- PostgreSQL
- Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/your-org/rtf-academy-backend.git
cd rtf-academy-backend
```

---

## 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Environment Variables

Create a `.env` file at the root of the project:

```bash
touch .env
```

Add the following variables:

```env
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/rtf_academy
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json

```

Make sure you have firebase-credentials.json in your root directory.

> Never commit your `.env` file to GitHub. It is already listed in `.gitignore`.

---

## 5. Database Setup

### Create the PostgreSQL database

Open your terminal and run:

```bash
psql -U postgres -c "CREATE DATABASE rtf_academy;"
```

### Run migrations to build the schema

```bash
python manage.py makemigrations
python manage.py migrate
```

### Seed the database with test data

```bash
python manage.py seed_db
```

This creates the following test scenario:

| Account | Email | Role |
|---|---|---|
| Admin | admin@rtfacademy.com | Admin |
| Student | student@rtfacademy.com | Student |

Two courses are seeded:
- **Digital Literacy for Refugee Youth** — fully completed, certificate issued
- **English Language Essentials** — in progress (33%), no certificate yet

---

## 6. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`.

---

## 7. Authentication

RTF Academy uses **stateless, Firebase-based authentication**. Django does not manage passwords or sessions.

### How it works

1. The Next.js frontend registers or logs in the user directly via the Firebase SDK.
2. Firebase returns an `idToken` to the client.
3. The client sends that token in the `Authorization` header on every API request:

```
Authorization: Bearer <firebase_idToken>
```

4. Our custom `FirebaseAuthentication` middleware verifies the token on every protected request. If the user does not exist in PostgreSQL yet, it is automatically created — this is called **Lazy Provisioning**.

### There is no `POST /api/register/` endpoint

Registration is handled entirely by Firebase on the frontend. The first time a new user hits any protected endpoint, their profile is silently created in the database.

> For login analytics, use the Firebase Console — Django does not track `last_login`.

---

## 9. Exporting Seed Data in JSON format
  
```bash
python manage.py dumpdata users courses quizzes progress certificates --indent 4 > rtf_master_seed.json
```
