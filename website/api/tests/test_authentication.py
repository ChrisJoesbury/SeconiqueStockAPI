# =============================================================================
# SeconiqueStockAPI | tests/test_authentication.py
# =============================================================================
# Authentication tests: CustomAPIKeyAuthentication.
# Run with: python manage.py test api.tests.test_authentication
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
# Get Rest Framework test files
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_api_key.models import APIKey
# Get API files
from api.models import UserProfile
from api.authentication import CustomAPIKeyAuthentication

# Test the CustomAPIKeyAuthentication class
class CustomAPIKeyAuthenticationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="pass")
        UserProfile.objects.create(user=self.user, cust_ID="CUST01")
        self.api_key_obj, self.raw_key = APIKey.objects.create_key(name="CUST01_apiuser")
        self.auth = CustomAPIKeyAuthentication()
        self.factory = RequestFactory()

    def _make_request(self, header_value):
        return self.factory.get('/', HTTP_AUTHORIZATION=header_value)

    def test_valid_key_returns_correct_user(self):
        request = self._make_request(f"Api-Key {self.raw_key}")
        result = self.auth.authenticate(request)
        self.assertIsNotNone(result)
        user, _ = result
        self.assertEqual(user, self.user)

    def test_missing_authorization_header_returns_none(self):
        request = self.factory.get('/')
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_empty_authorization_header_returns_none(self):
        request = self._make_request('')
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_wrong_prefix_returns_none(self):
        request = self._make_request(f"Bearer {self.raw_key}")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_invalid_key_raises_authentication_failed(self):
        request = self._make_request("Api-Key completely-invalid-key")
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_key_name_with_underscore_in_username(self):
        user2 = User.objects.create_user(username="user_with_underscore", password="pass")
        UserProfile.objects.create(user=user2, cust_ID="CUST02")
        _, raw_key2 = APIKey.objects.create_key(name="CUST02_user_with_underscore")
        request = self._make_request(f"Api-Key {raw_key2}")
        result = self.auth.authenticate(request)
        self.assertIsNotNone(result)
        user, _ = result
        self.assertEqual(user, user2)


# Run this module's tests when file is executed directly
if __name__ == '__main__':
    from django.test.utils import get_runner
    from django.conf import settings
    runner = get_runner(settings)(verbosity=2)
    failures = runner.run_tests(['api.tests.test_authentication'])
    sys.exit(1 if failures else 0)
