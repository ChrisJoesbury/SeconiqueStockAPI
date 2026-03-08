# templates/

This directory contains all Django HTML templates for the project's web-facing pages. Templates are located here (rather than inside the app) as they are shared across the project.

The path is registered in `settings.py` under `TEMPLATES[0]["DIRS"]`. **Tested on:** Django 6.0.1.

---

## 📁 Contents

```
templates/
├── login.html                        # User login page
├── register.html                     # New user registration page
├── profile.html                      # User profile — view/edit details and manage API key
├── csv_download.html                 # Simple HTML page for non-technical CSV downloads
└── drf_spectacular/
    └── swagger_ui.html               # Custom Swagger UI documentation page
```

---

## 📝 Template Descriptions

### `login.html`
Renders the login form. Conditionally shows a link to the registration page based on the `registration_enabled` flag from `SiteSettings`.

**View:** `CustomLoginView` — URL: `/login/`

---

### `register.html`
Renders the user registration form (`UserRegistrationForm`). Only accessible when registration is enabled in `SiteSettings`. Redirects to `/profile/` on success.

**View:** `register` — URL: `/register/`

---

### `profile.html`
The authenticated user's profile page. Displays:
- Account details (username, email, name, company)
- Edit profile form
- API key status — generate or delete a key
- Verification modal if the account has no `cust_ID` assigned yet
- One-time display of a newly generated API key (passed via session)

**View:** `profile` — URL: `/profile/`

---

### `csv_download.html`
A simple page that allows non-technical users to enter their API key and download stock levels as a CSV file without needing API clients. Uses JavaScript (`csrf.js`) to make the authenticated request.

**View:** `csv_download_page` — URL: `/csv-download/`

---

### `drf_spectacular/swagger_ui.html`
Overrides the default drf-spectacular Swagger UI template. Customised to inject the authenticated user's API key into the Swagger UI `Authorize` dialog automatically, so users can test endpoints directly from the docs page without manually entering their key.

**View:** `SwaggerWithUser` / login-required `TemplateView` — URL: `/api/docs/`
