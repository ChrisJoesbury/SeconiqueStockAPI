# api/

This is the main Django application. It contains all models, views, serializers, authentication logic, and forms for the SeconiqueStockAPI platform.

**Tested on:** Python 3.13+, Django 6.0.1, Django REST Framework 3.15+ (see root [README.md](../../../README.md) for full stack).

---

## 📁 Files

| File | Purpose |
|---|---|
| `models.py` | Database models and read-only DB views |
| `views.py` | API views, user registration, profile, and CSV download |
| `serializers.py` | DRF serializers — controls JSON output shape |
| `authentication.py` | Custom API key authentication class |
| `forms.py` | Django forms for registration and profile update |
| `pagination.py` | Custom pagination class (default limit/offset) |
| `swagger_view.py` | Custom Swagger UI view with user-specific schema |
| `spectacular_auth_extension.py` | drf-spectacular extension for API key auth scheme |
| `admin.py` | Django admin registrations |
| `apps.py` | App configuration |
| `tests/` | Test suite — see [tests/README.md](tests/README.md) for details |
| `urls.py` | App-level URL patterns (if used) |
| `migrations/` | Database migration history |

---

## 🧪 Tests

The **`tests/`** directory contains the full test suite for the api app, split into separate modules:

| Module | File | Coverage |
|---|---|---|
| Models | [test_models.py](tests/test_models.py) | StockLevels, UserProfile, SiteSettings (13 tests) |
| Forms | [test_forms.py](tests/test_forms.py) | UserRegistrationForm (9 tests) |
| Authentication | [test_authentication.py](tests/test_authentication.py) | CustomAPIKeyAuthentication (6 tests) |
| Serializers | [test_serializers.py](tests/test_serializers.py) | StockLevelsSerializer (4 tests) |
| Views | [test_views.py](tests/test_views.py) | Home, stock levels API/CSV, registration, profile (27 tests) |

Tests run against an in-memory SQLite database — no `.env` or external database required.

- **Run all tests:** from the `website/` directory: `python manage.py test api`
- **Run one module:** from `website/`: e.g. `python manage.py test api.tests.test_models` (use module path without `.py`; add `--verbosity=2` for per-test output)
- **Run one file directly:** from the repo root, set env vars then run e.g. `python website/api/tests/test_models.py` (each file is runnable on its own)
- **Documentation:** see **[tests/README.md](tests/README.md)** for full layout, run commands, and per-file coverage.

---

## 🗄️ Models

### `stocklevels`
The core data model. Stores product stock information loaded from internal systems.

| Field | Type | Description |
|---|---|---|
| `company` | CharField | Company identifier for data filtering |
| `partNum` | CharField | Product part number |
| `partDesc` | CharField | Product description |
| `rangeName` | CharField | Product range name |
| `groupDesc` | CharField | Product group description |
| `subGroupDesc` | CharField | Product sub-group description |
| `stockLev` | IntegerField | Current stock level |
| `lastUpdatedDT` | DateTimeField | Timestamp of last update |

### Read-only DB Views (unmanaged)
These map to SQL views in the database and are used to populate filter dropdown endpoints.

| Model | DB View | Returns |
|---|---|---|
| `GroupDescView` | `groupDescView` | Distinct group descriptions |
| `SubGroupDescView` | `subGroupDescView` | Distinct sub-group descriptions |
| `RangeNameView` | `rangeNameView` | Distinct range names |

### `UserProfile`
Extends the built-in Django `User` with API-specific fields.

| Field | Description |
|---|---|
| `cust_ID` | Customer ID assigned by admin — required before an API key can be generated |
| `company_ID` | Used to filter stock data to the user's company only |
| `company_Name` | Display name of the user's company |
| `website` | User's website URL |
| `api_key` | Masked copy of the user's current API key (for display only) |

### `SiteSettings`
Singleton model controlling site-wide behaviour. Managed via the Django admin.

| Field | Description |
|---|---|
| `registration_enabled` | Controls whether the `/register/` page accepts new users |

---

## 🌐 Views & Endpoints

| View | URL | Auth | Description |
|---|---|---|---|
| `home` | `/` | None | Redirects to `/api/docs/` |
| `CustomLoginView` | `/login/` | None | Login page |
| `register` | `/register/` | None | Registration (if enabled via SiteSettings) |
| `profile` | `/profile/` | Login required | View/edit profile and manage API key |
| `StockLevelsListView` | `/stocklevels/` | API Key | Paginated, filterable stock levels JSON |
| `StockLevelsCSVDownloadView` | `/stocklevels/csv/` | API Key | Full stock levels CSV download |
| `GroupDescListAPI` | `/prodgroups/` | API Key | Distinct product group descriptions |
| `SubGroupDescListAPI` | `/prodsubgroups/` | API Key | Distinct sub-group descriptions |
| `RangeNameListAPI` | `/ranges/` | API Key | Distinct range names |
| `csv_download_page` | `/csv-download/` | None | Simple HTML page for CSV download |

---

## 🔐 Authentication

The `CustomAPIKeyAuthentication` class in `authentication.py` handles API key validation. It:

1. Reads the `Authorization` header expecting the format `Api-Key {key}`
2. Validates the key against the `APIKey` model (from `djangorestframework-api-key`)
3. Extracts the username from the key name (format: `{cust_id}_{username}`)
4. Returns the corresponding Django `User` object so stock data can be filtered per company

API keys are generated and managed on the `/profile/` page. A `cust_ID` must be assigned by an admin before a key can be generated.

---

## 🧩 Stock Level Filtering

The `StockLevelsFilter` class supports the following query parameters on `/stocklevels/`:

| Parameter | Type | Description |
|---|---|---|
| `partNum` | string | Exact match on part number |
| `rangeName` | string | Exact match on range name |
| `groupDesc` | string | Exact match on group description |
| `subGroupDesc` | string | Exact match on sub-group description |
| `sl_greaterThan` | integer | Stock level greater than value |
| `sl_lessThan` | integer | Stock level less than value |
| `sl_equalTo` | integer | Stock level equal to value |
