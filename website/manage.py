#!/usr/bin/env python
# =============================================================================
# SeconiqueStockAPI | manage.py
# =============================================================================
# Django's command-line utility for administrative tasks such as running the
# development server, applying migrations, creating superusers, and executing
# the test suite. Usage: python manage.py <command>
# =============================================================================
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
