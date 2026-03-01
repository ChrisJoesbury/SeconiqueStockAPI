# =============================================================================
# SeconiqueStockAPI | spectacular_auth_extension.py
# =============================================================================
# Registers CustomAPIKeyAuthentication with drf-spectacular's OpenAPI schema
# generator, exposing the correct API key security scheme definition in the
# generated OpenAPI schema and Swagger UI.
# =============================================================================

#Get drf-spectacular's OpenApiAuthenticationExtension base class
from drf_spectacular.extensions import OpenApiAuthenticationExtension

#Get the CustomAPIKeyAuthentication class defined in authentication.py
from .authentication import CustomAPIKeyAuthentication


class CustomAPIKeyAuthenticationExtension(OpenApiAuthenticationExtension):
    """Registers CustomAPIKeyAuthentication with drf-spectacular's OpenAPI schema generator."""
    target_class = CustomAPIKeyAuthentication
    name = 'ApiKeyAuth'

    def get_security_definition(self, auto_schema):
        """Return the OpenAPI security scheme definition for CustomAPIKeyAuthentication.

        Args:
            auto_schema (AutoSchema): The drf-spectacular auto-schema instance
                used during schema generation. Not used directly here but
                required by the extension interface.

        Returns:
            dict: An OpenAPI-compatible security scheme object describing an
                API key passed in the Authorization request header using the
                format 'Api-Key <your-key>'.
        """
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Use format: Api-Key <your-key>'
        }
