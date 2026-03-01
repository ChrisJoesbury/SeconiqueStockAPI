# =============================================================================
# SeconiqueStockAPI | urls.py
# =============================================================================
# URL routing for SeconiqueStockAPI. Maps all routes including authentication
# (login/register/logout), user profile management, REST API endpoints for stock
# data, and the drf-spectacular OpenAPI documentation interface.
# =============================================================================

#Get Django Stuff
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static


#Get Spectacular Stuff
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    #SpectacularRedocView,
)

#Get my views
from api.views import (
    home,
    profile,
    register,
    custom_login_view,
    csv_download_page,
    StockLevelsListView,
    StockLevelsCSVDownloadView,
    GroupDescListAPI,
    SubGroupDescListAPI,
    RangeNameListAPI
)
from api.swagger_view import SwaggerWithUser, CustomSpectacularAPIView


urlpatterns = [
    # ============================================
    # Admin Routes
    # ============================================
    path('admin/', admin.site.urls), # Django admin interface

    # ============================================
    # Home Route
    # ============================================
    path('', home, name="home"), # Redirects to API documentation page

    # ============================================
    # Authentication Routes
    # ============================================
    path("login/", custom_login_view, name="login"), # User login page
    path("register/", register, name="register"), # User registration page
    path("logout/", auth_views.LogoutView.as_view(), name="logout"), # User logout

    # ============================================
    # User Profile Routes
    # ============================================
    path("profile/", profile, name="profile"), # User profile page - view/edit profile and manage API keys

    # ============================================
    # CSV Download Routes
    # ============================================
    path("csv-download/", csv_download_page, name="csv-download"), # Simple HTML page for CSV download (non-technical users)

    # ============================================
    # API Endpoints - Stock Levels
    # ============================================
    path('stocklevels/', StockLevelsListView.as_view(), name='stocklevels'), # GET - List stock levels with filtering (requires API key)
    path('stocklevels/csv/', StockLevelsCSVDownloadView.as_view(), name='stocklevels-csv'), # GET - Download stock levels as CSV (requires API key)

    # ============================================
    # API Endpoints - Product Groups
    # ============================================
    path("prodgroups/", GroupDescListAPI.as_view(), name="prodgroups"), # GET - List product group descriptions (requires API key)
    path("prodsubgroups/", SubGroupDescListAPI.as_view(), name="prodsubgroups"), # GET - List product sub-group descriptions (requires API key)
    path("ranges/", RangeNameListAPI.as_view(), name="ranges"), # GET - List range names (requires API key)

    # ============================================
    # API Documentation Routes
    # ============================================
    path("api/schema/", CustomSpectacularAPIView.as_view(), name="schema"), # GET - OpenAPI schema endpoint (user-specific schema generation)
    path("api/docs/", login_required(TemplateView.as_view(template_name="drf_spectacular/swagger_ui.html")), name="swagger-ui"), # Swagger UI documentation page (requires login)
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS else None)
