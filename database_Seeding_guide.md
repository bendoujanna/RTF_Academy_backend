# RTF Academy: Database Seeding Guide

This guide explains how to set up, seed, and export the RTF Academy PostgreSQL database for local development.

---

## 1. Architecture Overview

Our PostgreSQL database is logically divided into 4 primary domains:

###  Identity Domain (`users` app)

- **`UserProfile`** : The core user table linked to Firebase. Contains `uid` (Firebase ID), `email`, `full_name`, and `role` (Admin/Student).

###  Content Domain (`courses` app)

- **`Course`** : The top-level LMS entity (Title, Description, Published Status).
- **`Module`** : Groupings within a course.
- **`Lesson`** : Individual learning materials (Text/Video) linked to a Module.

###  Assessment Domain (`quizzes` app)

- **`Quiz`** : Linked to a specific Module. Defines the passing threshold.
- **`Question`** : Linked to a Quiz.
- **`AnswerChoice`** : Linked to a Question. Includes the `is_correct` boolean flag.

### Progress and Records Domain (`progress` and `certificates` apps)

- **`Enrollment`** : Links a Student to a Course, tracking overall percentage.
- **`LessonCompletion`** : Tracks exactly which lessons a student has finished.
- **`QuizAttempt`** : Records the score and pass/fail status of a quiz taken by a student.
- **`StudentAnswer`** : (Linked to `QuizAttempt`) Records the exact choices a student made on a quiz.
- **`Certificate`** : The final issued credential, containing a unique verification code and S3 PDF link.

---

## 2. Architectural Note: Authentication and Registration

RTF Academy uses a **stateless, decoupled authentication model** via Firebase.

You will notice there is no `POST /api/register/` endpoint.

We use a pattern called **Lazy Provisioning** to ensure the database stays perfectly synced with Firebase without race conditions:

1. The Next.js client registers the user directly via the Firebase SDK and receives an `idToken`.
2. The client sends that token in the `Authorization: Bearer <token>` header to any protected Django API endpoint.
3. Our custom `FirebaseAuthentication` middleware intercepts the token, verifies the cryptographic signature, and silently auto-creates the `UserProfile` row in PostgreSQL if the UID does not already exist.

> **Note:** Because authentication is stateless, Django does not track `last_login` times. Rely on the Firebase Console for accurate user login analytics.

---

## 3. Prerequisites

Before seeding the database, ensure your local PostgreSQL server is running and your `core/settings.py` is configured with your database credentials.

Run the standard Django migration commands to build the tables in PostgreSQL:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 4. Hydrating the Database (The Master Seed)

We use a custom Django management command to inject a complete, interconnected test scenario into the database. The script is **idempotent**, meaning you can safely run it multiple times without duplicating data or crashing your database.

```bash
python manage.py seed_db
```

**What this creates:**

- 1 Admin User (`admin@rtfacademy.com`)
- 1 Student User (`student@rtfacademy.com`)
- 1 Course ("Backend Engineering Foundations") containing 1 Module and 1 Lesson
- 1 Assessment Quiz with sample Questions and Answer Choices
- Progress records, a simulated passing quiz attempt, and a generated Certificate

---

## 5. Exporting Data for the Frontend Team

You can generate a JSON dump of the seeded data:

```bash
python manage.py dumpdata users courses quizzes progress certificates --indent 4 > rtf_master_seed.json
```