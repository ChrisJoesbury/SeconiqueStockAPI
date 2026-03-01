# =============================================================================
# SeconiqueStockAPI | admin.py
# =============================================================================
# Django admin configuration. Registers UserProfile as an inline on the User
# model and configures a SiteSettings singleton admin that prevents creation of
# duplicate instances and disables deletion.
# =============================================================================

#Get Django files
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

#Get local files
from .models import UserProfile, SiteSettings

#Define admin site headers and titles
admin.site.site_header = "API Site Admin Portal"
admin.site.site_title = "API Site Admin Portal"
admin.site.index_title = "Welcome to the API Site Administration Portal"


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Prevents creation of a second SiteSettings instance and disables deletion."""

    def has_add_permission(self, request):
        """Allow creation only when no SiteSettings instance exists yet.

        Args:
            request (HttpRequest): The current admin request.

        Returns:
            bool: True if the SiteSettings table is empty (first-time setup),
                False if an instance already exists (enforces singleton).
        """
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Unconditionally deny deletion of the SiteSettings singleton.

        Args:
            request (HttpRequest): The current admin request.
            obj (SiteSettings | None): The object to be deleted, if any.

        Returns:
            bool: Always False — the singleton must not be removed via the admin.
        """
        return False
