# 🏥 Mini Hospital Management System (HMS)

A Django-based hospital management web app with doctor availability scheduling, patient appointment booking, and serverless email notifications.

---

## 📋 Project Info

| Field | Details |
|-------|---------|
| **Project Type** | Web Application |
| **Tech Stack** | Django + PostgreSQL + Serverless |
| **Environment** | WSL (Ubuntu) on Windows |
| **Status** | ✅ Running Successfully |
| **Date** | March 2026 |

---

## 📁 Project Structure

```
hms_project/
├── manage.py                    # Django management tool
├── requirements.txt             # Python package list
├── .env                         # Secret config (DB password, email, etc.)
├── .env.example                 # Template for .env
├── .gitignore
│
├── hms/                         # Django project settings
│   ├── settings.py              # Main config (DB, apps, auth, etc.)
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py
│
├── accounts/                    # User authentication app
│   ├── migrations/
│   ├── models.py                # Custom User model (role field)
│   ├── views.py                 # signup_view, login_view, logout_view
│   ├── forms.py                 # SignupForm, LoginForm
│   ├── urls.py                  # /accounts/signup/, /login/, /logout/
│   └── admin.py
│
├── appointments/                # Booking management app
│   ├── migrations/
│   ├── models.py                # Slot model, Booking model
│   ├── views.py                 # dashboard, add_slot, book_slot, delete_slot
│   ├── forms.py                 # SlotForm
│   ├── urls.py                  # /appointments/dashboard/, /add-slot/, /book/<id>/
│   └── admin.py
│
├── templates/                   # All HTML pages
│   ├── base.html                # Shared layout (navbar, styles)
│   ├── accounts/
│   │   ├── login.html
│   │   └── signup.html
│   └── appointments/
│       ├── doctor_dashboard.html
│       ├── patient_dashboard.html
│       ├── add_slot.html
│       └── book_slot.html
│
├── static/
│   └── style.css                # Extra global styles
│
└── email_service/               # Serverless email project (separate)
    ├── handler.py               # Lambda function (sends emails)
    ├── serverless.yml           # Serverless config
    ├── package.json
    └── .env                     # Email credentials
```

---

## 🔑 Key Features

- **Role-based authentication** — separate Doctor and Patient accounts with different dashboards
- **Doctor availability management** — doctors create time slots by date and time
- **Patient appointment booking** — patients browse available slots and book in one click
- **Race condition prevention** — database-level locking (`select_for_update`) ensures no double bookings
- **Email notifications** — welcome email on signup, confirmation email on booking
- **Serverless email service** — separate Python Lambda function using Serverless Framework

---

## 🗄️ System Architecture

Two independently running services communicate via HTTP:

| Service | Port | Technology | Responsibility |
|---------|------|------------|----------------|
| Django Web App | 8000 | Python / Django | Main app — auth, slots, bookings, UI |
| Email Service | 3000 | Python / Serverless Offline | Sends emails via Gmail SMTP |

### How the Services Connect

- When a user **signs up**, Django calls the email service at port 3000 with action `SIGNUP_WELCOME`
- When a **booking is confirmed**, Django calls the email service with action `BOOKING_CONFIRMATION`
- If the email service is down, the main app continues working — emails are non-blocking

---

## ⚙️ Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Backend Framework | Django | 4.2.x | Web app, routing, ORM, auth |
| Database | PostgreSQL | 14+ | Stores users, slots, bookings |
| Language | Python | 3.12 | Backend logic |
| Email Service | Serverless Framework | 3.40.0 | Lambda function for emails |
| Runtime (email) | Node.js | 20.20.1 | Runs serverless-offline |
| Environment | WSL Ubuntu | on Windows | Linux terminal on Windows |
| Virtual Env | Python venv | built-in | Isolates project packages |

---

## 🚀 Setup Instructions

> 📌 Follow every step in order on a fresh machine.

### PHASE 1 — Install Required Software

#### Step 1 — Install Python 3.10+

- Download from: https://www.python.org/downloads/
- **During install: check 'Add Python to PATH'** — this is critical

```bash
python --version
# Expected: Python 3.12.x
```

#### Step 2 — Install PostgreSQL

- Download from: https://www.postgresql.org/download/
- Set a password for the `postgres` user during install — remember it
- Default port: `5432` — leave as is

In WSL/Linux terminal:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo service postgresql start
```

#### Step 3 — Install Node.js 20

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify:
node --version   # v20.x.x
npm --version    # 9.x.x or 10.x.x
```

#### Step 4 — Install Serverless Framework V3

> V3 is used specifically because V4 requires a paid account.

```bash
sudo npm install -g serverless@3.38.0

# Verify:
serverless --version
# Expected: Framework Core: 3.x.x
```

---

### PHASE 2 — Project Setup

> ⚠️ All Django commands must be run from the `hms_project` folder where `manage.py` is located.

#### Step 5 — Extract the project ZIP

Extract `hms_project.zip` to your desired location (e.g. `D:\tungProject\`) and open a terminal inside the `hms_project` folder.

#### Step 6 — Create and activate virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/WSL):
source venv/bin/activate

# Activate (Windows CMD):
venv\Scripts\activate

# Your prompt should now show: (venv)
```

> ✅ You must activate the venv every time you open a new terminal to work on this project.

#### Step 7 — Install Python packages

```bash
pip install -r requirements.txt

# Verify Django installed:
python -m django --version
# Expected: 4.2.x
```

#### Step 8 — Create the PostgreSQL database

```bash
# Set password for postgres user:
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres123';"

# Create the database:
sudo -u postgres psql -c "CREATE DATABASE hms_db;"
```

#### Step 9 — Create and configure the .env file

```bash
cp .env.example .env
nano .env
```

The `.env` file should contain:

```
SECRET_KEY=django-insecure-<generated-random-string>
DEBUG=True
DB_NAME=hms_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
EMAIL_FROM=yourgmail@gmail.com
EMAIL_PASSWORD=your16charapppassword
SERVERLESS_EMAIL_URL=http://localhost:3000/dev/send-email
```

Generate a `SECRET_KEY` with:

```bash
python -c "import secrets; print('django-insecure-' + secrets.token_urlsafe(40))"
```

> ⚠️ No quotes around values. No spaces around `=` signs. No comment lines (`#`) in the `.env` file.

#### Step 10 — Run database migrations

```bash
python manage.py makemigrations accounts
python manage.py makemigrations appointments
python manage.py migrate
```

Expected output:
```
Applying accounts.0001_initial... OK
Applying appointments.0001_initial... OK
Applying auth.0001_initial... OK
...
```

#### Step 11 — Create superuser (admin account)

```bash
python manage.py createsuperuser
# Enter username, email, and password when prompted
# Example: username=admin, email=admin@gmail.com, password=admin123
```

---

### PHASE 3 — Email Service Setup

#### Step 12 — Navigate to email_service folder

```bash
cd email_service
```

#### Step 13 — Install Node.js dependencies

```bash
npm install
```

#### Step 14 — Configure serverless.yml with email credentials

Open `serverless.yml` and set your email values in the `environment` section:

```yaml
service: hms-email-service
frameworkVersion: '>=3'

provider:
  name: aws
  runtime: python3.11
  region: ap-south-1
  environment:
    EMAIL_FROM: yourgmail@gmail.com
    EMAIL_PASSWORD: your16charapppassword

plugins:
  - serverless-offline

custom:
  serverless-offline:
    httpPort: 3000
    host: localhost

functions:
  sendEmail:
    handler: handler.send_notification
    events:
      - http:
          path: /send-email
          method: post
          cors: true
```

> 📌 **Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App Passwords → Generate a 16-character password for Mail.

---

## ▶️ Running the Project

> ⚠️ You need **two terminal windows** open at the same time — one for each service.

### Terminal 1 — Start Email Service

```bash
cd /path/to/hms_project/email_service
serverless offline
```

Expected output:
```
Running "serverless" from node_modules
Environment: linux, node 20.20.1, framework 3.40.0...
Server ready: http://localhost:3000 🚀
POST - http://localhost:3000/dev/send-email
```

### Terminal 2 — Start Django App

```bash
cd /path/to/hms_project
source venv/bin/activate
sudo service postgresql start
python manage.py runserver
```

Expected output:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## 🌐 Access URLs

| Page | URL |
|------|-----|
| Home (redirects to dashboard) | http://127.0.0.1:8000/ |
| Sign Up | http://127.0.0.1:8000/accounts/signup/ |
| Login | http://127.0.0.1:8000/accounts/login/ |
| Dashboard (Doctor or Patient) | http://127.0.0.1:8000/appointments/dashboard/ |
| Add Slot (Doctor only) | http://127.0.0.1:8000/appointments/add-slot/ |
| Django Admin Panel | http://127.0.0.1:8000/admin/ |
| Email Service (local) | http://localhost:3000/dev/send-email |

---

## 👤 User Roles

| Role | Capabilities |
|------|-------------|
| **Doctor** | Sign up, log in, add availability slots, view their bookings, delete unbooked slots |
| **Patient** | Sign up, log in, view all available slots, book a slot, view their bookings |
| **Admin** | Access Django admin panel at `/admin/` to manage all data |

---

## 🔄 Features Walkthrough

### Doctor Workflow

1. Go to `/accounts/signup/` and create an account with **role: Doctor**
2. Redirected to Doctor Dashboard — shows stats: total slots, appointments
3. Click **+ Add Availability Slot**
4. Pick a date, start time, end time — click Save
5. Slot appears in the dashboard table with status **Available** (green)
6. After a patient books, status changes to **Booked** (red)
7. Doctor can delete unbooked slots using the Delete button

### Patient Workflow

1. Go to `/accounts/signup/` and create an account with **role: Patient**
2. Redirected to Patient Dashboard — shows available slots from all doctors
3. Click **Book** on any available slot
4. Review appointment details on confirmation page
5. Click **Confirm Booking**
6. Slot disappears from available list immediately
7. Booking appears in **My Bookings** section
8. Confirmation email is sent to both patient and doctor

### Email Notifications

| Trigger | Action | Recipients |
|---------|--------|------------|
| User signs up | `SIGNUP_WELCOME` — welcome email sent | The new user |
| Booking confirmed | `BOOKING_CONFIRMATION` — confirmation email sent | Patient + Doctor |

### Race Condition Prevention

When two patients try to book the same slot simultaneously, the system uses database-level row locking:

```python
# In appointments/views.py
with transaction.atomic():
    slot = Slot.objects.select_for_update().get(id=slot_id)
    if slot.is_booked:
        messages.error(request, 'Slot was just booked by someone else.')
        return redirect('dashboard')
    # Proceed with booking...
```

This ensures only one booking is ever created per slot, even under concurrent requests.

---

## 🗃️ Database Schema

| Table | Key Fields | Description |
|-------|-----------|-------------|
| `accounts_user` | id, username, email, role, password | All users — doctors and patients |
| `appointments_slot` | id, doctor_id, date, start_time, end_time, is_booked | Doctor availability slots |
| `appointments_booking` | id, slot_id, patient_id, created_at | Confirmed appointments |

### Inspecting the Database

```bash
# Connect:
sudo -u postgres psql hms_db
```

| What to check | SQL Query |
|---------------|-----------|
| List all tables | `\dt` |
| All users with roles | `SELECT id, username, email, role FROM accounts_user;` |
| All availability slots | `SELECT * FROM appointments_slot;` |
| All bookings | `SELECT * FROM appointments_booking;` |
| Bookings with full details | `SELECT b.id, p.username AS patient, d.username AS doctor, s.date, s.start_time, s.end_time FROM appointments_booking b JOIN appointments_slot s ON b.slot_id = s.id JOIN accounts_user p ON b.patient_id = p.id JOIN accounts_user d ON s.doctor_id = d.id;` |
| Exit psql | `\q` |

---

## ⚡ Daily Commands Cheatsheet

### Every time you start working

```bash
# 1. Start PostgreSQL
sudo service postgresql start

# 2. Terminal 1 — Start email service
cd /path/to/hms_project/email_service
serverless offline

# 3. Terminal 2 — Start Django
cd /path/to/hms_project
source venv/bin/activate
python manage.py runserver

# 4. Open browser
# http://127.0.0.1:8000
```

### Setting up on a new machine

```bash
# Install system dependencies
sudo apt update && sudo apt install postgresql postgresql-contrib -y
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g serverless@3.38.0

# Start PostgreSQL and create DB
sudo service postgresql start
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres123';"
sudo -u postgres psql -c "CREATE DATABASE hms_db;"

# Project setup
cd hms_project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env   # fill in your values

# Run migrations
python manage.py makemigrations accounts
python manage.py makemigrations appointments
python manage.py migrate
python manage.py createsuperuser

# Email service
cd email_service
npm install
# Edit serverless.yml with your email credentials

# Run (two terminals)
serverless offline          # Terminal 1
python manage.py runserver  # Terminal 2
```

---

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Connection refused (port 5432) | `sudo service postgresql start` |
| No configuration file found | `cd` into `email_service/` first |
| `(venv)` missing from prompt | `source venv/bin/activate` |
| Serverless V4 login prompt | `npm install -g serverless@3.38.0` |
| Port 8000 already in use | `python manage.py runserver 8080` |
| No changes in makemigrations | `python manage.py makemigrations accounts appointments` |

### Issues Faced During Initial Setup

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| `ModuleNotFoundError: dotenv` | Virtual env recreated without packages | `pip install -r requirements.txt` |
| `manage.py` already exists | Ran `django-admin` inside already-setup folder | No need to run `django-admin` — project files already exist in zip |
| `accounts` conflicts with existing module | Ran `startapp` on existing app | Do not run `startapp` — apps already exist in zip |
| PostgreSQL connection refused | PostgreSQL not installed in WSL | `sudo apt install postgresql && sudo service postgresql start` |
| No changes detected in makemigrations | `AUTH_USER_MODEL` not set in `settings.py` | Add `AUTH_USER_MODEL = 'accounts.User'` to `settings.py` |
| Serverless V4 requires license | npm installed latest V4 by default | `npm install -g serverless@3.38.0` to force V3 |
| `No version found for 3` | `serverless.yml` had `frameworkVersion: '3'` | Changed to `frameworkVersion: '>=3'` |
| Cannot resolve variable `EMAIL_FROM` | `serverless.yml` used `${env:}` syntax but no system env vars set | Hardcoded values directly in `serverless.yml` environment section |
| `(venv)` not showing after `cd` | Virtual env not reactivated in new terminal | Run `source venv/bin/activate` every time |
