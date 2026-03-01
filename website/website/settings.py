# =============================================================================
# SeconiqueStockAPI | settings.py
# =============================================================================
# Django project settings. Handles environment-based configuration via environs,
# dual database setup (SQLite for development, MySQL/Google Cloud SQL for
# production), REST framework, drf-spectacular, and production security headers.
# =============================================================================


from pathlib import Path
from environs import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env = Env()
env.read_env(BASE_DIR / '.env')  # Read from .env file if it exists


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Must be set via SECRET_KEY in your .env file
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# Must be explicitly set to True in your .env file for development.
DEBUG = env.bool('DEBUG', default=False)

# ALLOWED_HOSTS: List of hosts/domains that this Django site can serve
# Get from environment variable (comma-separated)
# Default to localhost for development, but MUST be set explicitly in production
if DEBUG:
    # In development mode, allow localhost by default
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
else:
    # In production mode, ALLOWED_HOSTS must be explicitly set via .env
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
    if not ALLOWED_HOSTS:
        raise ValueError(
            "ALLOWED_HOSTS must be set when DEBUG=False. "
            "Please set ALLOWED_HOSTS in your .env file with your domain(s)."
        )

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "api",
    'rest_framework',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'rest_framework_api_key',
]

#Set up REST Framework with drf-spectacular and API key authentication
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.authentication.CustomAPIKeyAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # add this
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework_api_key.permissions.HasAPIKey"
    ],
    "DEFAULT_PAGINATION_CLASS": "api.pagination.CustomLimitOffsetPagination",
}

# API Endpoint Descriptions - Centralized descriptions for Swagger documentation
API_ENDPOINT_DESCRIPTIONS = {
    "stocklevels": (
        "Retrieve a list of stock levels with optional filtering.\n\n"
        "Available filters:\n"
        "- partNum: Filter by exact part number\n"
        "- rangeName: Filter by range name\n"
        "- groupDesc: Filter by group description\n"
        "- subGroupDesc: Filter by sub-group description\n"
        "- sl_greaterThan: Stock level greater than value\n"
        "- sl_lessThan: Stock level less than value\n"
        "- sl_equalTo: Stock level equal to value"
    ),
    "stocklevels_csv": (
        "Download stock levels as a CSV file."
    ),
    "prodgroups": (
        "Retrieve a list of all product group descriptions relating to the stocklevels endpoint.\n\n"
        "- Sorted alphabetically, these can be used to filter the stocklevels endpoint."
    ),
    "prodsubgroups": (
        "Retrieve a list of all product sub-group descriptions relating to the stocklevels endpoint.\n\n"
        "- Sorted alphabetically, these can be used to filter the stocklevels endpoint."
    ),
    "ranges": (
        "Retrieve a list of all range names relating to the stocklevels endpoint.\n\n"
        "- Sorted alphabetically, these can be used to filter the stocklevels endpoint."
    ),
}

# drf-spectacular settings for API documentation and schema generation
SPECTACULAR_SETTINGS = {
    "TITLE": "Seconique Furniture Stock API System",
    "VERSION": "1.0.2",
    "DESCRIPTION": (
        "Welcome to the API documentation page, below are the endpoints with example responses.\n\n"
        "An API key is required for all endpoints and can be generated on the profile page.\n\n"
        "To test, click the Authorize button and enter your API key in the format: <code>Api-Key {your-key}</code>"
    ),
    "SECURITY": [{"ApiKeyAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Use format: `Authorization: Api-Key {your-key}`",
            },
        }
    },

    "AUTHENTICATION_WHITELIST": ["api.authentication.CustomAPIKeyAuthentication"],
    "SERVE_AUTHENTICATION": [],
    "SERVE_PERMISSIONS": [],
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "defaultModelsExpandDepth": 0,
    },
    # Disable schema caching to ensure user-specific schemas
    "SCHEMA_PATH_PREFIX": None,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', #sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', #CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', #User auth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'website.urls'

# Tell Django where your login page actually is
LOGIN_URL = "/login/"

# (optional but nice) where to go after login/logout
LOGIN_REDIRECT_URL = "/api/docs/"
LOGOUT_REDIRECT_URL = "/login/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],   # <-- this must include your templates folder
        "APP_DIRS": True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Google Cloud SQL Configuration
# Connection details from: docs/google-cloud-instance-db details.txt
# Instance: seconique-stocklevels-api
# Connection Name: storied-deck-469407-s6:europe-west2:seconique-stocklevels-api

# Try to use Google Cloud SQL if credentials are available, otherwise fall back to SQLite
USE_CLOUD_DB = env.bool('USE_CLOUD_DB', default=False)

if USE_CLOUD_DB:
    # Configure pymysql as the MySQL backend.
    # pymysql is a pure-Python MySQL client; Django's backend expects mysqlclient and
    # performs a version check that pymysql does not satisfy on its own.
    # Spoofing version_info is the standard workaround — see:
    # https://github.com/PyMySQL/PyMySQL/issues/790
    try:
        import pymysql
        pymysql.version_info = (2, 2, 1, "final", 0)
        pymysql.install_as_MySQLdb()
    except ImportError:
        raise ImportError(
            "pymysql is required when USE_CLOUD_DB=True. "
            "Install it with: pip install pymysql"
        )

    # Google Cloud SQL MySQL 8.4 configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env.str('DB_NAME'),
            'USER': env.str('DB_USER'),
            'PASSWORD': env.str('DB_PASSWORD'),
            'HOST': env.str('DB_HOST'),
            'PORT': env.str('DB_PORT', default='3306'),
            'OPTIONS': {
                'connect_timeout': 10,
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # Local SQLite database (development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Folder containing your own static files (optional)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Folder where Django collects all static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Production security settings
# These are only enforced when DEBUG=False to avoid breaking local development.
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/
if not DEBUG:
    # Redirect all HTTP requests to HTTPS
    SECURE_SSL_REDIRECT = True

    # Tell browsers to only connect via HTTPS for 1 year (including subdomains)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Prevent session cookie being sent over plain HTTP
    SESSION_COOKIE_SECURE = True

    # Prevent CSRF cookie being sent over plain HTTP
    CSRF_COOKIE_SECURE = True

    # Prevent browsers from guessing content types
    SECURE_CONTENT_TYPE_NOSNIFF = True
