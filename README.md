## Todo App Backend (FastAPI + MongoDB)

### Overview

This is a minimal, production-style monolith backend for a Todo App built with **FastAPI**, **MongoDB**, and **Motor**.  
It supports:

- **Email + password auth**
- **Email + OTP auth**
- **Role-based authorization** (`user`, `admin`)
- **Todo CRUD** (per-user)
- **Admin reports** (basic metrics and recent activity)

The codebase is structured to be **simple, clean, and beginner-friendly** while following common production patterns (routes → services → repositories → database).

---

### Project Structure

- `app/main.py` – FastAPI app, router wiring, startup/shutdown, admin seeding.
- `app/core/` – core infrastructure:
  - `config.py` – settings via environment variables (`.env`).
  - `database.py` – MongoDB client and collection helpers.
  - `security.py` – password hashing and JWT helpers.
- `app/models/` – internal document models for MongoDB.
- `app/schemas/` – Pydantic request/response models for the API.
- `app/repositories/` – MongoDB access (Motor) for users, otps, todos.
- `app/services/` – business logic (auth, todos, admin, email).
- `app/dependencies/` – FastAPI dependencies (current user/admin).
- `app/routes/` – FastAPI routers (auth, todos, admin, health).
- `app/utils/` – small utilities (time helpers).

---

### Requirements

- Python 3.10+ (recommended)
- Local MongoDB running (default URI: `mongodb://localhost:27017`)

---

### Setup Instructions

1. **Clone the repository** (or open the backend folder).

2. **Create and activate a virtual environment** (example with `venv`):

```bash
python -m venv .venv
source .venv/bin/activate  # on macOS/Linux
# .venv\Scripts\activate   # on Windows
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:

- Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

- Adjust values as needed (Mongo URI, DB name, JWT secret, admin credentials, optional SMTP).

5. **Ensure MongoDB is running locally**:

- Default URI is `mongodb://localhost:27017`.
- On macOS with Homebrew, you can run:

```bash
brew services start mongodb-community
```

Or use `mongod` directly if installed another way.

---

### Running the FastAPI Server

From the project root (where `app/` lives):

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

### Admin Seeding (Initial Admin Account)

On **application startup**, the app:

1. Connects to MongoDB.
2. Checks if a user with `ADMIN_EMAIL` exists.
3. If not, creates an admin user with:
   - `email`: `ADMIN_EMAIL` (default `admin@todo.com`)
   - `password`: `ADMIN_PASSWORD` (default `todo@pass`)
   - `role`: `admin`
   - `is_active=True`, `is_verified=True`

These values are configurable via `.env`:

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

**Important**: Change these defaults for any real environment.

---

### Main API Endpoints

#### Auth (Email + Password + OTP)

- `POST /api/v1/auth/register`
  - Body: `{ "name", "email", "password" }`
  - Registers a new user (`role="user"`), returns JWT + user info.

- `POST /api/v1/auth/login`
  - Body: `{ "email", "password" }`
  - Logs in existing user, returns JWT + user info.

- `POST /api/v1/auth/request-otp`
  - Body: `{ "email" }`
  - Generates and stores an OTP, sends via email service abstraction.
  - Always responds with a generic success message.

- `POST /api/v1/auth/verify-otp`
  - Body: `{ "email", "otp_code" }`
  - Verifies OTP:
    - If user exists: logs them in (marks `is_verified=True` if needed).
    - If user does not exist: creates a new `user` and logs them in.

- `GET /api/v1/auth/me`
  - Header: `Authorization: Bearer <token>`
  - Returns current user’s profile.

#### Todos (Authenticated User)

- `POST /api/v1/todos`
  - Create a todo for the current user.

- `GET /api/v1/todos`
  - List all todos for the current user.

- `GET /api/v1/todos/{todo_id}`
  - Get a single todo belonging to the current user.

- `PUT /api/v1/todos/{todo_id}`
  - Update title/description/`is_completed` for the current user’s todo.

- `DELETE /api/v1/todos/{todo_id}`
  - Delete the current user’s todo.

- `PATCH /api/v1/todos/{todo_id}/complete`
  - Mark todo as completed.

- `PATCH /api/v1/todos/{todo_id}/incomplete`
  - Mark todo as incomplete.

Ownership is enforced in the repository layer by always filtering on `user_id`.

#### Admin Auth & Reports

- `POST /api/v1/admin/auth/login`
  - Body: `{ "email", "password" }`
  - Only succeeds if the user exists with `role="admin"`.
  - Returns JWT + admin user info.

- `GET /api/v1/admin/reports/summary`
  - Header: `Authorization: Bearer <admin-token>`
  - Returns:
    - `total_users`
    - `total_todos`
    - `total_completed_todos`
    - `total_pending_todos`
    - `recent_users` (last 5)
    - `recent_todos` (last 5)
    - `user_todo_counts` (per-user aggregates)

#### Health

- `GET /`
  - Simple welcome message.

- `GET /health`
  - Returns `{ "status": "ok" }`.

---

### OTP Email Sending (Dev-Friendly)

The OTP email sending is abstracted in `app/services/email_service.py`:

- If **SMTP** settings are **not** configured:
  - OTPs are printed to the console like:
    - `[DEV OTP] Email: test@example.com, OTP: 123456`
- If SMTP settings are configured in `.env`:
  - Real emails are sent using Python’s `smtplib`.

SMTP-related variables (optional):

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`

This lets you start with console-based OTPs for local development and switch to real email later without changing auth logic.

---

### Sample Local Flow

1. **Register and login with password**
   - `POST /api/v1/auth/register` → get JWT.
   - Use the token with `Authorization: Bearer <token>` for protected endpoints.

2. **Create and manage todos**
   - `POST /api/v1/todos` to create.
   - `GET /api/v1/todos` to list.
   - `PATCH /api/v1/todos/{id}/complete` to mark complete.

3. **Admin login & reports**
   - Use seeded admin (`ADMIN_EMAIL` / `ADMIN_PASSWORD`) to:
     - `POST /api/v1/admin/auth/login` → get admin JWT.
   - Call:
     - `GET /api/v1/admin/reports/summary` with admin token.

4. **OTP login flow (dev)**
   - `POST /api/v1/auth/request-otp` with an email.
   - Check console for `[DEV OTP]` line.
   - `POST /api/v1/auth/verify-otp` with `email` and `otp_code` from console → receive JWT.

---

### Learning Notes (How Things Are Structured)

- **Routes** (`app/routes/*`):
  - Only handle HTTP details (paths, status codes, dependencies).
  - Delegate work to services.
- **Services** (`app/services/*`):
  - Contain business rules (auth logic, todo ownership, admin rules).
  - Call repositories for DB access.
- **Repositories** (`app/repositories/*`):
  - Contain all MongoDB queries using Motor.
  - Work with Python dicts / basic shapes.
- **Core** (`app/core/*`):
  - Shared infrastructure for config, DB, and security (hashing + JWT).

Read the code in this order if you want to learn the flow:

1. `app/core/config.py`, `app/core/security.py`, `app/core/database.py`
2. `app/schemas/*`
3. `app/repositories/*`
4. `app/services/*`
5. `app/dependencies/auth_dependencies.py`
6. `app/routes/*`
7. `app/main.py`

This should give you a clear picture of how a simple, production-style FastAPI backend is structured.
