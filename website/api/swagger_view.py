# =============================================================================
# SeconiqueStockAPI | swagger_view.py
# =============================================================================
# Custom Swagger UI view that extends SpectacularSwaggerView to inject the
# authenticated user's username into the template context, enabling personalised
# display in the API documentation interface.
# =============================================================================

#Get DRF Spectacular views
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView


class SwaggerWithUser(SpectacularSwaggerView):
    template_name = "drf_spectacular/swagger_ui.html"

    def get(self, request, *args, **kwargs):
        """Render the Swagger UI page with the current user's username in context.

        Args:
            request (HttpRequest): The authenticated incoming HTTP request.
            *args: Additional positional arguments passed by the URL dispatcher.
            **kwargs: Additional keyword arguments passed by the URL dispatcher.

        Returns:
            TemplateResponse: The Swagger UI response with 'username' added to
                context_data, making it available to the template for personalised
                display (e.g. greeting or profile info in the UI header).

        Contract:
            - Delegates to the parent get() to generate the OpenAPI schema and
              base context, then augments context_data before returning.
            - If the user is anonymous, get_username() returns an empty string;
              the template should handle this gracefully.
        """
        response = super().get(request, *args, **kwargs)
        response.context_data = response.context_data or {}
        response.context_data["username"] = request.user.get_username()
        return response


class CustomSpectacularAPIView(SpectacularAPIView):
    """
    Custom schema view — uses base class functionality unchanged.
    Subclassed to allow future customisation of schema generation behaviour
    without modifying third-party code directly.
    """
    pass
