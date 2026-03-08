# SeconiqueStockAPI

![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![Django](https://img.shields.io/badge/Django-6.0.1-green)
![DRF](https://img.shields.io/badge/DRF-API-red)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

SeconiqueStockAPI is a stock API platform designed to provide **self‑service, real‑time stock level access for customers**. It standardises product and inventory data, enabling customers to integrate stock feeds into their systems using modern REST endpoints or legacy‑friendly CSV downloads.

---

## 🚀 Overview

The platform provides a **RESTful API** built with Django and Django REST Framework (DRF). It aggregates stock information from internal systems, applies customer‑specific filters, and returns consistent JSON or CSV data.

Key capabilities include:
- Customisable queries and filters
- Standardised product/stock fields
- Pagination with configurable limits
- API key authentication
- Company-scoped data filtering
- CSV export for legacy systems

---

## 🛠️ Technologies Used

### Languages
- Python 3.13+

### Frameworks
- Django 6.0.1
- Django REST Framework (DRF)

### API & Authentication
- djangorestframework-api-key — API key authentication
- django-filter — query filtering

### API Schema & Documentation
- drf-spectacular — OpenAPI 3 generation
- drf-spectacular-sidecar — Swagger UI / Redoc assets

### Database
- MySQL (production)
- SQLite (development)

### Configuration & Utilities
- environs — environment variable management
- inflection — string utilities
- uritemplate — URI template expansion

### Security / Crypto
- cryptography — encryption & signing utilities

### Tested on
- **Python** 3.13+
- **Django** 6.0.1
- **Django REST Framework** 3.15+
- **SQLite** (development and test suite)
- **MySQL** 8.x (production / Cloud SQL)

---

## ✨ Features

- **Real‑time Stock Feeds** via JSON and CSV
- **Advanced Filtering** on groups, ranges, stock levels, part numbers
- **CSV Support** for legacy integrations
- **API‑Key Authentication** for controlled access
- **Company-Scoped Data** — each API key automatically filters results to the customer's own stock
- **Standardised Output Format** across endpoints

---

## 🧰 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-org/SeconiqueStockAPI.git
cd SeconiqueStockAPI
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file
A `.env.example` template is provided in the `website/` directory. Copy it and fill in your values:

```bash
cp website/.env.example website/.env       # macOS/Linux
copy website\.env.example website\.env     # Windows
```

The `.env` file is required — the application will not start without it. At minimum, set `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

For local development the defaults in `.env.example` are sufficient. For production, also set:
```env
DEBUG=False
USE_CLOUD_DB=True
ALLOWED_HOSTS=yourdomain.com
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
```

### 5. Apply migrations
```bash
cd website
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```

### 7. Access the API
- API Docs: http://127.0.0.1:8000/api/docs/
- Admin Panel: http://127.0.0.1:8000/admin/

---

## 🧪 Running Tests

The test suite lives in **`website/api/tests/`**, split into separate modules: `test_models.py`, `test_forms.py`, `test_authentication.py`, `test_serializers.py`, and `test_views.py`. It covers models, forms, authentication, serializers, and all API and view endpoints. Tests use Django's built-in test runner with an in-memory SQLite database — no `.env` file or external database required.

From the `website/` directory (with your virtual environment activated), set the required environment variables and run:

**macOS / Linux:**
```bash
SECRET_KEY=django-insecure-test-key DEBUG=True USE_CLOUD_DB=False python manage.py test api
```

**Windows (PowerShell):**
```powershell
$env:SECRET_KEY="django-insecure-test-key"; $env:DEBUG="True"; $env:USE_CLOUD_DB="False"; python manage.py test api
```

For verbose output (each test name as it runs), add `--verbosity=2`:
```bash
SECRET_KEY=django-insecure-test-key DEBUG=True USE_CLOUD_DB=False python manage.py test api --verbosity=2
```
```powershell
$env:SECRET_KEY="django-insecure-test-key"; $env:DEBUG="True"; $env:USE_CLOUD_DB="False"; python manage.py test api --verbosity=2
```

The suite contains **59 tests** in five modules:

| Module | File | Tests |
|---|---|---|
| Models | `test_models.py` | 13 |
| Forms | `test_forms.py` | 9 |
| Authentication | `test_authentication.py` | 6 |
| Serializers | `test_serializers.py` | 4 |
| Views | `test_views.py` | 27 |

- **Single module** (from `website/`): use the module path **without** `.py`, e.g. `python manage.py test api.tests.test_models` (or `test_forms`, `test_authentication`, `test_serializers`, `test_views`). Add `--verbosity=2` to see each test name.
- **Single file directly** (from repo root): set env vars as above, then e.g. `python website/api/tests/test_models.py`.

See **`website/api/tests/README.md`** for per-file test classes, direct-run examples, and full run instructions.

---

## ☁️ Post-Deployment Steps

After pulling changes to the cloud server, run the following to collect Django and DRF internal static assets (admin panel, Swagger UI etc.):

```bash
python manage.py collectstatic
```

---

## 🔑 First-time Setup

Create a superuser to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Log in at `/admin/` to:
- Enable user registration via **Site Settings**
- Assign a **Customer ID** (`cust_ID`) to user accounts — required before an API key can be generated

---

## 📌 Pagination

Pagination applies to all JSON endpoints (`/stocklevels/`, `/prodgroups/`, `/prodsubgroups/`, `/ranges/`). It does **not** apply to `/stocklevels/csv/`, which always returns all records.

| Parameter | Type | Description |
|---|---|---|
| `limit` | int | Number of results to return. Defaults to `1000` via Swagger UI; unlimited from other clients. Use `all` or `unlimited` for no limit. |
| `offset` | int | Number of records to skip before returning results. Defaults to `0`. |

**Example:**
```http
GET /stocklevels/?limit=50&offset=0
```

---

## 📚 API Endpoints

All endpoints require an API key passed in the `Authorization` header:
```http
Authorization: Api-Key <your_api_key>
```

---

### GET /stocklevels/

Returns a paginated, filterable list of stock levels in JSON format.

#### Filters

| Parameter | Type | Description |
|---|---|---|
| `groupDesc` | string | Filter by group description (exact match) |
| `subGroupDesc` | string | Filter by sub-group description (exact match) |
| `partNum` | string | Filter by part number (exact match) |
| `rangeName` | string | Filter by range name (exact match) |
| `sl_equalTo` | integer | Stock level equal to value |
| `sl_greaterThan` | integer | Stock level greater than value |
| `sl_lessThan` | integer | Stock level less than value |
| `limit` | integer | Results per page |
| `offset` | integer | Results to skip |

#### Examples

Filter by group and sub‑group:
```http
GET /stocklevels/?groupDesc=Bedroom&subGroupDesc=Wardrobes
```

Filter by part number:
```http
GET /stocklevels/?partNum=ABC123
```

Filter by range name:
```http
GET /stocklevels/?rangeName=SOFAS
```

Stock level comparisons:
```http
GET /stocklevels/?sl_greaterThan=5
GET /stocklevels/?sl_lessThan=20
GET /stocklevels/?sl_equalTo=10
```

Combined filters:
```http
GET /stocklevels/?rangeName=SOFAS&groupDesc=Living%20Room&sl_greaterThan=5&limit=100&offset=0
```

---

### GET /stocklevels/csv/

Downloads all stock levels as a CSV file. No pagination — always returns the full dataset for the authenticated customer.

```http
GET /stocklevels/csv/
```

---

### GET /prodgroups/

Returns a sorted list of all distinct product group descriptions. Use these values to filter the `/stocklevels/` endpoint.

```http
GET /prodgroups/
```

| Parameter | Type | Description |
|---|---|---|
| `limit` | int | Max number of records |
| `offset` | int | Records to skip |

---

### GET /prodsubgroups/

Returns a sorted list of all distinct product sub-group descriptions. Use these values to filter the `/stocklevels/` endpoint.

```http
GET /prodsubgroups/
```

| Parameter | Type | Description |
|---|---|---|
| `limit` | int | Max number of records |
| `offset` | int | Records to skip |

---

### GET /ranges/

Returns a sorted list of all distinct range names. Use these values to filter the `/stocklevels/` endpoint.

```http
GET /ranges/
```

| Parameter | Type | Description |
|---|---|---|
| `limit` | int | Max number of records |
| `offset` | int | Records to skip |

---

## 🔐 Authentication

API keys are generated by users on their profile page (`/profile/`) after their account has been verified by an administrator. Keys are passed in the request header:

```http
Authorization: Api-Key <your_api_key>
```

Each key is scoped to a customer — stock data is automatically filtered to return only that customer's inventory.

---

## 📖 Documentation

Additional documentation is in the **`docs/`** directory:

- **[User Manual](docs/)** — End-user guide for the SeconiqueStockAPI application  
- **[Admin User Manual](docs/)** — Administrator guide for managing and configuring the application  
- **Database schema** — Sanitised MySQL DDL (see `docs/README.md` for details)

---

## 📁 Folder Structure

```
SeconiqueStockAPI/
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── docs/               # User manuals (PDF), database schema, and docs README
├── postman/            # Postman collection for API testing
├── seed/               # Data-loading scripts and fixtures
└── website/            # Django project root
    ├── .env.example    # Environment variable template — copy to .env
    ├── api/            # Django app — models, views, serializers, authentication, tests/
    ├── static/         # Source static files (CSS, JS, images)
    ├── templates/      # HTML templates
    └── website/        # Project configuration (settings, URLs, WSGI)
```

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 📬 Contact

**Chris Joesbury**  
Wolverhampton, West Midlands  
Email: chrisjoesbury@gmail.com
