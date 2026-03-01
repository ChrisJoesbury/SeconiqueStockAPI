# website/

This is the root of the Django project. It contains all application source code, configuration, templates, and static assets.

---

## 📁 Directory Structure

```
website/
├── api/                  # Django app — models, views, serializers, authentication
├── static/               # Source static files (CSS, JS, images)
├── templates/            # HTML templates
├── website/              # Django project configuration (settings, URLs, WSGI)
├── manage.py             # Django management entry point
├── .gitignore            # Git exclusion rules
└── README.md             # This file
```

---

## ⚙️ Environment Variables

All sensitive configuration is loaded from a `.env` file in this directory. This file is **not committed to the repository**. Create it before running the project.

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Enable debug mode | `True` / `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `USE_CLOUD_DB` | Use MySQL instead of SQLite | `True` / `False` |
| `DB_NAME` | MySQL database name | `mydb` |
| `DB_USER` | MySQL username | `myuser` |
| `DB_PASSWORD` | MySQL password | `mypassword` |
| `DB_HOST` | MySQL host | `myhost.mysql.example.com` |
| `DB_PORT` | MySQL port (optional, default: 3306) | `3306` |

---

## 🚀 Running Locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file (see Environment Variables above)

# 4. Apply migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` — redirects to the Swagger API docs.

---

## ☁️ Cloud Deployment (PythonAnywhere)

After pulling changes to the server:

```bash
# Install/update dependencies
pip install -r requirements.txt

# Apply any new migrations
python manage.py migrate

# Collect static files (Django admin, DRF, Swagger UI assets)
python manage.py collectstatic
```

Ensure the `.env` file is present on the server with `DEBUG=False`, `USE_CLOUD_DB=True`, and `ALLOWED_HOSTS` set to your domain.

---

## 🔑 First-time Setup

1. Create a superuser to access the Django admin panel:
   ```bash
   python manage.py createsuperuser
   ```
2. Log in at `/admin/` and enable user registration via **Site Settings** if required.
