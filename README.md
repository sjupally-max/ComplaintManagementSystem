# ComplaiNext — Complaint Management System

A professional Flask complaint-management application for a Python Developer internship portfolio. It includes secure user authentication, role-based administration, complaint CRUD, file uploads, filtering, search, pagination, and dashboard analytics.

## Features

- Secure registration and login with Werkzeug password hashing
- User and admin dashboards with Chart.js analytics
- Complaint submission, editing, deletion, category/status/priority filters, and keyword search
- Admin-only status updates and access to every complaint
- SQLite database via SQLAlchemy ORM
- Server-side validation, CSRF protection, flash feedback, responsive Bootstrap 5 UI
- Attachments: PNG, JPG, JPEG, GIF, PDF, DOC, DOCX (up to 8 MB)

## Project structure

```text
ComplaintManagementSystem/
├── app.py, config.py, models.py, routes.py, auth.py, forms.py
├── requirements.txt
├── templates/
└── static/css, static/js, static/uploads/
```

## Installation and running in Visual Studio Code

1. Open this project folder in VS Code: **File → Open Folder**.
2. Open the integrated terminal (**Terminal → New Terminal**) and create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install packages:

   ```powershell
   pip install -r requirements.txt
   ```

4. Start the application:

   ```powershell
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser. Register a normal account, then submit complaints.

## Create an administrator

Register a user first, stop the server, and use this small one-time command from the project terminal:

```powershell
python -c "from app import create_app; from models import db, User; app=create_app(); app.app_context().push(); u=User.query.filter_by(email='your-email@example.com').first(); u.is_admin=True; db.session.commit()"
```

Replace the email address with the registered email, then restart the server and sign in. The **Admin Panel** will become visible.

## Production note

Set a strong `SECRET_KEY`, turn off Flask debug mode, use a production WSGI server, and store uploads outside public static storage before deployment.
