# =============================================================================
# SeconiqueStockAPI | apps.py
# =============================================================================
# Django AppConfig for the 'api' application. Imports spectacular_auth_extension
# on app startup to ensure the OpenAPI authentication scheme is registered with
# drf-spectacular before the schema is generated.
# =============================================================================

#Get Django files
from django.apps import AppConfig

#Define the ApiConfig class
class ApiConfig(AppConfig):
    #Set the name of the app
    name = 'api'

    def ready(self):
        #Import the spectacular_auth_extension
        from . import spectacular_auth_extension  # noqa: F401
        #This is to ensure the extension is loaded when the app is ready