# website/website/

This is the Django **project configuration package** (the inner `website/` folder). It contains the project-level settings, URL routing, and server entry points.

---

## 📁 Files

| File | Purpose |
|---|---|
| `settings.py` | All project configuration — database, installed apps, static files, auth, etc. |
| `urls.py` | Root URL configuration — maps all URL patterns to views |
| `wsgi.py` | WSGI entry point for production deployment (used by PythonAnywhere) |
| `asgi.py` | ASGI entry point (included for portability; not used in current deployment) |
| `__init__.py` | Marks this directory as a Python package |

---

## ⚙️ settings.py

All sensitive values are loaded from a `.env` file via `environs`. No secrets are hardcoded.

### Key settings sections

| Section | Notes |
|---|---|
| `SECRET_KEY` | Loaded from `.env` — required, no default |
| `DEBUG` | Defaults to `True` in development; set `False` in production |
| `ALLOWED_HOSTS` | Defaults to `localhost`/`127.0.0.1` in debug; must be set via `.env` in production |
| `INSTALLED_APPS` | Includes `api`, `rest_framework`, `drf_spectacular`, `rest_framework_api_key` |
| `DATABASES` | SQLite in development; switches to MySQL when `USE_CLOUD_DB=True` |
| `STATICFILES_DIRS` | Points to `website/static/` (source files) |
| `STATIC_ROOT` | Points to `website/staticfiles/` (collected output — not committed to repo) |
| `REST_FRAMEWORK` | Uses `CustomAPIKeyAuthentication`, `HasAPIKey` permission, custom pagination |
| `SPECTACULAR_SETTINGS` | API title, version, description, and security scheme for Swagger UI |

---

## 🌐 urls.py

The root URL configuration. All application routes are defined here.

| URL | View | Notes |
|---|---|---|
| `/` | `home` | Redirects to `/api/docs/` |
| `/admin/` | Django admin | |
| `/login/` | `CustomLoginView` | |
| `/logout/` | `LogoutView` | |
| `/register/` | `register` | Controlled by `SiteSettings.registration_enabled` |
| `/profile/` | `profile` | Login required |
| `/csv-download/` | `csv_download_page` | |
| `/stocklevels/` | `StockLevelsListView` | API key required |
| `/stocklevels/csv/` | `StockLevelsCSVDownloadView` | API key required |
| `/prodgroups/` | `GroupDescListAPI` | API key required |
| `/prodsubgroups/` | `SubGroupDescListAPI` | API key required |
| `/ranges/` | `RangeNameListAPI` | API key required |
| `/api/schema/` | `CustomSpectacularAPIView` | OpenAPI schema |
| `/api/docs/` | `SwaggerWithUser` | Swagger UI — login required |

---

## 🖥️ wsgi.py

Used by PythonAnywhere (and other WSGI servers) to serve the application in production. Sets `DJANGO_SETTINGS_MODULE` to `website.settings`.
