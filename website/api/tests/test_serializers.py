# =============================================================================
# SeconiqueStockAPI | tests/test_serializers.py
# =============================================================================
# Serializer tests: StockLevelsSerializer (company field visibility, fields).
# Run with: python manage.py test api.tests.test_serializers
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
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
# Get API files
from api.models import StockLevels, UserProfile
from api.serializers import StockLevelsSerializer

# Test the StockLevelsSerializer (company field visibility and output fields)
class StockLevelsSerializerTest(TestCase):

    def setUp(self):
        self.item = StockLevels.objects.create(
            company="CO001",
            partNum="PART001",
            partDesc="Part One",
            rangeName="RangeA",
            groupDesc="GroupA",
            subGroupDesc="SubA",
            stockLev=5,
        )
        self.scoped_user = User.objects.create_user(username="scoped", password="pass")
        UserProfile.objects.create(user=self.scoped_user, company_ID="CO001")

        self.admin_user = User.objects.create_user(username="admin_user", password="pass")
        UserProfile.objects.create(user=self.admin_user, company_ID="")

    def _make_request(self, user):
        request = RequestFactory().get('/')
        request.user = user
        return request

    def test_scoped_user_does_not_see_company_field(self):
        request = self._make_request(self.scoped_user)
        serializer = StockLevelsSerializer(self.item, context={'request': request})
        self.assertNotIn('company', serializer.data)

    def test_admin_user_sees_company_field(self):
        request = self._make_request(self.admin_user)
        serializer = StockLevelsSerializer(self.item, context={'request': request})
        self.assertIn('company', serializer.data)
        self.assertEqual(serializer.data['company'], 'CO001')

    def test_all_standard_fields_present(self):
        request = self._make_request(self.scoped_user)
        serializer = StockLevelsSerializer(self.item, context={'request': request})
        for field in ['partNum', 'partDesc', 'rangeName', 'groupDesc', 'subGroupDesc', 'stockLev', 'lastUpdatedDT']:
            self.assertIn(field, serializer.data)

    def test_field_values_are_correct(self):
        request = self._make_request(self.scoped_user)
        data = StockLevelsSerializer(self.item, context={'request': request}).data
        self.assertEqual(data['partNum'], 'PART001')
        self.assertEqual(data['stockLev'], 5)
        self.assertEqual(data['groupDesc'], 'GroupA')


# Run this module's tests when file is executed directly
if __name__ == '__main__':
    from django.test.utils import get_runner
    from django.conf import settings
    runner = get_runner(settings)(verbosity=2)
    failures = runner.run_tests(['api.tests.test_serializers'])
    sys.exit(1 if failures else 0)
