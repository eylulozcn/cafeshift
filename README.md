# CafeShift

A weekly shift-planning web application built with Django and MySQL,
inspired by the scheduling workflow at the café where I work.

The application helps a manager assign employees to shifts, review
planned working hours, and copy the weekly schedule for sharing.

## Features

- Manager-only access using Django staff authentication
- Employee management through the Django admin panel
- Weekly schedule with previous/next week navigation
- Two daily shifts: 12:00–18:00 and 18:00–00:00
- One employee per shift
- Create, update, and remove assignments from a weekly form
- Weekly shift counts and planned working hours per employee
- Copy the saved schedule as plain text
- MySQL persistence and a database uniqueness constraint
- Atomic weekly updates

## Tech Stack

- Python
- Django
- MySQL and mysqlclient
- HTML, CSS, and JavaScript
- Git

## Current Scope

This version supports manual scheduling for a single café.
Each shift is counted as six planned hours, without deducting breaks.
Employee availability and automatic scheduling are not implemented yet.

## Local Setup — Windows Command Prompt

Developed with Python 3.14, Django 6.0, and MySQL 8.0.

1. Download or clone this repository and open its folder.
2. Create and activate a virtual environment:

   python -m venv .venv
   .venv\Scripts\activate.bat

3. Install dependencies:

   python -m pip install -r requirements.txt

4. Create a MySQL database named cafeshift using utf8mb4.
   Create a dedicated database user and grant it privileges on cafeshift.

5. Copy the example configuration:

   copy .env.example .env

6. Update .env with your database credentials and a unique
   DJANGO_SECRET_KEY. You can generate a key with:

   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

7. Create the database tables and a manager account:

   python manage.py migrate
   python manage.py createsuperuser

8. Start the local development server:

   python manage.py runserver

9. Open http://127.0.0.1:8000/admin/ and add employees.
   Open http://127.0.0.1:8000/ to prepare the weekly schedule.

## Configuration

Real credentials belong in .env, which is excluded from Git.
.env.example contains placeholders only.

This project currently uses local development settings.
Production deployment requires separate configuration.

## Planned Improvements

- Recurring employee availability
- Scheduling conflict checks
- Automatic shift suggestions
- Automated tests for scheduling behavior