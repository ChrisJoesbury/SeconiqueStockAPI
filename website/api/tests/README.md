# api/tests/

Test suite for the SeconiqueStockAPI **api** app. All tests use Django's built-in test runner with an in-memory SQLite database — no `.env` file or external MySQL connection is required.

**Tested on:** Python 3.13+, Django 6.0.1, Django REST Framework 3.15+, in-memory SQLite.

---

## 🚀 Running the tests

From the **`website/`** directory (project root, where `manage.py` lives), with your virtual environment activated:

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

**Run a single test module** (from `website/`). Use the module path **without** `.py` (e.g. `api.tests.test_serializers`, not `test_serializers.py`):
```bash
python manage.py test api.tests.test_models
python manage.py test api.tests.test_forms
python manage.py test api.tests.test_authentication
python manage.py test api.tests.test_serializers
python manage.py test api.tests.test_views
# Optional: add --verbosity=2 to see each test name
```

**Run a single test file directly** (from the **repo root**; each file configures Django and runs its own tests when executed):
```powershell
# Windows (PowerShell) — set env vars then run the file
$env:SECRET_KEY="django-insecure-test-key"; $env:DEBUG="True"; $env:USE_CLOUD_DB="False"
python website/api/tests/test_models.py
```
```bash
# macOS / Linux
SECRET_KEY=django-insecure-test-key DEBUG=True USE_CLOUD_DB=False python website/api/tests/test_models.py
```

---

## 📁 Layout

| File | Purpose |
|---|---|
| `__init__.py` | Marks this directory as the `api.tests` package so Django discovers tests here |
| `test_models.py` | Model tests: StockLevels, UserProfile, SiteSettings (13 tests). Runnable directly. |
| `test_forms.py` | Form tests: UserRegistrationForm validation (9 tests). Runnable directly. |
| `test_authentication.py` | Authentication tests: CustomAPIKeyAuthentication (6 tests). Runnable directly. |
| `test_serializers.py` | Serializer tests: StockLevelsSerializer (4 tests). Runnable directly. |
| `test_views.py` | View tests: home, stock levels API/CSV, registration, profile (27 tests). Runnable directly. |
| `README.md` | This file |

**Total: 59 tests** across 5 test modules. Each test file includes an `if __name__ == '__main__':` block so it can be run directly from the repo root (Django is configured before imports; the test runner runs at the end of the file).

---

## 📋 Test coverage by file

### test_models.py (13 tests)
| Test class | Description |
|---|---|
| `StockLevelsModelTest` | `str`, defaults, field storage, `lastUpdatedDT` |
| `UserProfileModelTest` | `str`, user link, optional fields |
| `SiteSettingsModelTest` | Singleton behaviour, registration toggle, `str` |

### test_forms.py (9 tests)
| Test class | Description |
|---|---|
| `UserRegistrationFormTest` | Validation (password rules, duplicates, required fields) |

### test_authentication.py (6 tests)
| Test class | Description |
|---|---|
| `CustomAPIKeyAuthenticationTest` | Valid key, missing/wrong header, invalid key, key name format |

### test_serializers.py (4 tests)
| Test class | Description |
|---|---|
| `StockLevelsSerializerTest` | Company field visibility (scoped vs admin), field presence and values |

### test_views.py (27 tests)
| Test class | Description |
|---|---|
| `HomeViewTest` | Home redirects to `/api/docs/` |
| `StockLevelsAPITest` | API key required, 200 with key, company scoping, filters, response shape |
| `StockLevelsCSVTest` | CSV auth, content-type, disposition, headers, data, scoping |
| `RegistrationViewTest` | Disabled redirect, enabled form, user/profile creation, redirects, validation |
| `ProfileViewTest` | Login required, accessible when logged in, profile update saves |

---

## 📌 Notes

- **No fixtures:** Tests create their own data in `setUp()` and use the in-memory test database.
- **API key tests** use `rest_framework_api_key.models.APIKey` and the custom `CustomAPIKeyAuthentication` class.
- **Direct run:** Each test file has two `if __name__ == '__main__':` blocks: the first configures Django before any imports (so the file can be executed directly); the second runs this module’s tests and exits. When tests are run via `manage.py test api`, neither block runs.
- For project-wide test instructions and counts, see the root [README.md](../../../README.md) “Running Tests” section.
