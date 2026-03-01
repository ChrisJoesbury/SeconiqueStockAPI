# =============================================================================
# SeconiqueStockAPI | models.py
# =============================================================================
# Defines all database models: StockLevels (stock data), GroupDescView,
# SubGroupDescView, RangeNameView (read-only DB views), UserProfile
# (extends Django's User), and SiteSettings (singleton site configuration).
# =============================================================================

#Get Django files
from django.db import models
from django.contrib.auth.models import User


class StockLevels(models.Model):
    """Stores product stock level records, scoped per company."""
    # Field names use camelCase to match legacy column naming from the source ERP system.
    company = models.CharField(max_length=10, default="xxxxxxxxxx")
    partNum = models.CharField(max_length=11, default="xxxxxxxxxxx")
    partDesc = models.CharField(max_length=150, default="xxxxxxxxxx")
    rangeName = models.CharField(max_length=100, default="xxxxxxxxxx")
    groupDesc = models.CharField(max_length=100, default="xxxxxxxxxx")
    subGroupDesc = models.CharField(max_length=100, default="xxxxxxxxxx")
    stockLev = models.IntegerField(default=0)
    lastUpdatedDT = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_stocklevels'  # Preserves the existing table name after class rename
        verbose_name = 'Stock Level'
        verbose_name_plural = 'Stock Levels'

    def __str__(self):
        """Return a human-readable string representation of the stock record.

        Returns:
            str: The part number and description in the format 'partNum - partDesc'.
        """
        return f"{self.partNum} - {self.partDesc}"


class GroupDescView(models.Model):
    """Read-only model backed by the groupDescView database view."""
    groupDesc = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = "groupDescView"


class SubGroupDescView(models.Model):
    """Read-only model backed by the subGroupDescView database view."""
    subGroupDesc = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = "subGroupDescView"


class RangeNameView(models.Model):
    """Read-only model backed by the rangeNameView database view."""
    rangeName = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = "rangeNameView"


class UserProfile(models.Model):
    """Extends the built-in User model with API key and company information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cust_ID = models.CharField(max_length=6, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)  # Masked display key — not the real key
    company_ID = models.CharField(max_length=10, blank=True, null=True)
    company_Name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        """Return the username of the associated User.

        Returns:
            str: The username of the linked Django User instance.
        """
        return self.user.username


class SiteSettings(models.Model):
    """
    Singleton model for site-wide settings.
    Only one instance should ever exist — pk=1 is enforced on every save.
    """
    registration_enabled = models.BooleanField(
        default=False,
        help_text="Enable user registration. When enabled, users can create accounts via the register page."
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        """Return a fixed label used in the Django admin interface.

        Returns:
            str: The string 'Site Settings'.
        """
        return "Site Settings"

    def save(self, *args, **kwargs):
        """Override save to enforce the singleton pattern by always using pk=1.

        Args:
            *args: Passed through to the parent save method.
            **kwargs: Passed through to the parent save method.

        Contract:
            Regardless of how this instance was created, pk is always set to 1
            before saving, ensuring only one row can ever exist in the database.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Return the singleton SiteSettings instance, creating it if it does not exist.

        Returns:
            SiteSettings: The single SiteSettings instance (always pk=1).

        Contract:
            Safe to call at any time. Will never raise DoesNotExist — if no
            instance exists, one is created with default values.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
