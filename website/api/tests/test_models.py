# =============================================================================
# SeconiqueStockAPI | tests/test_models.py
# =============================================================================
# Model tests: StockLevels, UserProfile, SiteSettings.
# Run with: python manage.py test api.tests.test_models
# =============================================================================

# Configure Django when run directly (must run before Django imports below)
if __name__ == '__main__':
    import os
    import sys
    _website_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _website_dir not in sys.path:
        sys.path.insert(0, _website_dir)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
    import django
    django.setup()

# Get Django test files
from django.test import TestCase
from django.contrib.auth.models import User
# Get API files
from api.models import StockLevels, UserProfile, SiteSettings

# Test the StockLevels model
class StockLevelsModelTest(TestCase):

    def setUp(self):
        self.item = StockLevels.objects.create(
            company="TESTCO",
            partNum="ABC123",
            partDesc="Test Part",
            rangeName="TestRange",
            groupDesc="TestGroup",
            subGroupDesc="TestSubGroup",
            stockLev=10,
        )

    def test_str_representation(self):
        self.assertEqual(str(self.item), "ABC123 - Test Part")

    def test_default_stock_level(self):
        item = StockLevels.objects.create()
        self.assertEqual(item.stockLev, 0)

    def test_last_updated_set_on_create(self):
        self.assertIsNotNone(self.item.lastUpdatedDT)

    def test_fields_stored_correctly(self):
        self.assertEqual(self.item.company, "TESTCO")
        self.assertEqual(self.item.partNum, "ABC123")
        self.assertEqual(self.item.stockLev, 10)


# Test the UserProfile model
class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="TestPass1!")
        self.profile = UserProfile.objects.create(user=self.user, company_Name="Acme Ltd")

    def test_str_representation(self):
        self.assertEqual(str(self.profile), "testuser")

    def test_profile_linked_to_user(self):
        self.assertEqual(self.profile.user, self.user)

    def test_optional_fields_default_to_null(self):
        self.assertIsNone(self.profile.cust_ID)
        self.assertIsNone(self.profile.api_key)
        self.assertIsNone(self.profile.company_ID)


# Test the SiteSettings singleton model
class SiteSettingsModelTest(TestCase):

    def test_singleton_load_returns_same_instance(self):
        s1 = SiteSettings.load()
        s2 = SiteSettings.load()
        self.assertEqual(s1.pk, s2.pk)

    def test_only_one_instance_created(self):
        SiteSettings.load()
        SiteSettings.load()
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_str_representation(self):
        s = SiteSettings.load()
        self.assertEqual(str(s), "Site Settings")

    def test_registration_disabled_by_default(self):
        s = SiteSettings.load()
        self.assertFalse(s.registration_enabled)

    def test_save_always_uses_pk_1(self):
        s = SiteSettings(registration_enabled=True)
        s.save()
        self.assertEqual(s.pk, 1)

    def test_registration_can_be_toggled(self):
        s = SiteSettings.load()
        s.registration_enabled = True
        s.save()
        reloaded = SiteSettings.load()
        self.assertTrue(reloaded.registration_enabled)


# Run this module's tests when file is executed directly
if __name__ == '__main__':
    from django.test.utils import get_runner
    from django.conf import settings
    runner = get_runner(settings)(verbosity=2)
    failures = runner.run_tests(['api.tests.test_models'])
    sys.exit(1 if failures else 0)
