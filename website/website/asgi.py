# =============================================================================
# SeconiqueStockAPI | asgi.py
# =============================================================================
# ASGI entry point for async-capable deployment. Exposes the Django application
# as the module-level 'application' variable required by ASGI-compatible servers
# such as Daphne or Uvicorn.
# =============================================================================

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

application = get_asgi_application()
