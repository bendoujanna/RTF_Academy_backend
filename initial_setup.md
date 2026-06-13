# RTF Academy — Backend Initial Setup Guide
 
## Prerequisites
 
- Python 3.x
- PostgreSQL

---
 
## Getting Started
 
### 1. Clone the Repository
 
```bash
git clone https://github.com/bendoujanna/RTF_Academy_backend.git
cd RTF_Academy_backend
```
 
### 2. Set Up a Virtual Environment
 
**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
 
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
 
### 3. Install Dependencies
 
```bash
pip install -r requirements.txt
```
 
---
 
## Environment Configuration
 
Create a `.env` file in the project root
---
 
## Database Setup
 
Run migrations to initialize the database schema:
 
```bash
python manage.py makemigrations
python manage.py migrate
```
 
---
 
## Run the Development Server
 
```bash
python manage.py runserver
```
 
---
 
## Project Structure
 
| App | Responsibility |
|---|---|
| `core/` | Settings, WSGI/ASGI, root URL routing |
| `users/` | Custom user model, Firebase UID integration, RBAC |
| `courses/` | Courses, modules, and lessons |
| `quizzes/` | Questions, grading logic, and scoring |
| `progress/` | Enrollments, analytics, and sequence gating |
| `certificates/` | Credential generation and document indexing |