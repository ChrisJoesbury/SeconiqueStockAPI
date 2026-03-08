# =============================================================================
# SeconiqueStockAPI | tests/test_views.py
# =============================================================================
# View tests: home, stock levels API/CSV, registration, profile.
# Run with: python manage.py test api.tests.test_views
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
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
# Get Rest Framework test files
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey
# Get API files
from api.models import StockLevels, UserProfile, SiteSettings

# Test the home view redirect to API docs
class HomeViewTest(TestCase):

    def test_home_redirects_to_api_docs(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/api/docs/', fetch_redirect_response=False)


# Test the stock levels JSON API endpoint (auth, scoping, filters)
class StockLevelsAPITest(TestCase):

    def _get_results(self, response):
        """Handle both paginated {'results': [...]} and plain list responses."""
        if isinstance(response.data, list):
            return response.data
        return response.data.get('results', response.data)

    def setUp(self):
        self.user = User.objects.create_user(username="apitest", password="pass")
        self.profile = UserProfile.objects.create(
            user=self.user, cust_ID="CUST01", company_ID="CO001"
        )
        self.api_key_obj, self.raw_key = APIKey.objects.create_key(name="CUST01_apitest")

        StockLevels.objects.create(
            company="CO001", partNum="P001", partDesc="Desc 1",
            rangeName="Range1", groupDesc="Group1", subGroupDesc="Sub1", stockLev=10
        )
        StockLevels.objects.create(
            company="CO001", partNum="P002", partDesc="Desc 2",
            rangeName="Range2", groupDesc="Group2", subGroupDesc="Sub2", stockLev=0
        )
        # Item for a different company — should be hidden from scoped user
        StockLevels.objects.create(
            company="OTHER", partNum="P003", partDesc="Other Co Item",
            rangeName="Range3", groupDesc="Group3", subGroupDesc="Sub3", stockLev=5
        )

    def _authed_client(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Api-Key {self.raw_key}")
        return client

    def test_stocklevels_requires_api_key(self):
        response = APIClient().get(reverse('stocklevels'))
        self.assertEqual(response.status_code, 403)

    def test_stocklevels_returns_200_with_valid_key(self):
        response = self._authed_client().get(reverse('stocklevels'))
        self.assertEqual(response.status_code, 200)

    def test_stocklevels_company_scoping_hides_other_companies(self):
        response = self._authed_client().get(reverse('stocklevels'))
        results = self._get_results(response)
        part_numbers = [item['partNum'] for item in results]
        self.assertIn('P001', part_numbers)
        self.assertIn('P002', part_numbers)
        self.assertNotIn('P003', part_numbers)

    def test_stocklevels_filter_by_groupDesc(self):
        response = self._authed_client().get(reverse('stocklevels') + '?groupDesc=Group1')
        results = self._get_results(response)
        self.assertTrue(len(results) > 0)
        self.assertTrue(all(item['groupDesc'] == 'Group1' for item in results))

    def test_stocklevels_filter_by_partNum(self):
        response = self._authed_client().get(reverse('stocklevels') + '?partNum=P001')
        results = self._get_results(response)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['partNum'], 'P001')

    def test_stocklevels_filter_sl_greater_than(self):
        response = self._authed_client().get(reverse('stocklevels') + '?sl_greaterThan=5')
        results = self._get_results(response)
        self.assertTrue(all(item['stockLev'] > 5 for item in results))

    def test_stocklevels_filter_sl_less_than(self):
        response = self._authed_client().get(reverse('stocklevels') + '?sl_lessThan=5')
        results = self._get_results(response)
        self.assertTrue(all(item['stockLev'] < 5 for item in results))

    def test_stocklevels_filter_sl_equal_to(self):
        response = self._authed_client().get(reverse('stocklevels') + '?sl_equalTo=10')
        results = self._get_results(response)
        self.assertTrue(all(item['stockLev'] == 10 for item in results))

    def test_stocklevels_response_contains_expected_fields(self):
        response = self._authed_client().get(reverse('stocklevels'))
        results = self._get_results(response)
        self.assertTrue(len(results) > 0)
        first = results[0]
        for field in ['partNum', 'partDesc', 'rangeName', 'groupDesc', 'subGroupDesc', 'stockLev']:
            self.assertIn(field, first)


# Test the stock levels CSV download endpoint
class StockLevelsCSVTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="csvtest", password="pass")
        self.profile = UserProfile.objects.create(
            user=self.user, cust_ID="CUST02", company_ID="CO002"
        )
        self.api_key_obj, self.raw_key = APIKey.objects.create_key(name="CUST02_csvtest")
        StockLevels.objects.create(
            company="CO002", partNum="CSV001", partDesc="CSV Part",
            rangeName="RangeX", groupDesc="GroupX", subGroupDesc="SubX", stockLev=3
        )

    def _authed_client(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Api-Key {self.raw_key}")
        return client

    def test_csv_requires_api_key(self):
        response = APIClient().get(reverse('stocklevels-csv'))
        self.assertEqual(response.status_code, 403)

    def test_csv_returns_200_with_valid_key(self):
        response = self._authed_client().get(reverse('stocklevels-csv'))
        self.assertEqual(response.status_code, 200)

    def test_csv_content_type_is_text_csv(self):
        response = self._authed_client().get(reverse('stocklevels-csv'))
        self.assertIn('text/csv', response['Content-Type'])

    def test_csv_has_attachment_content_disposition(self):
        response = self._authed_client().get(reverse('stocklevels-csv'))
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('stocklevels.csv', response['Content-Disposition'])

    def test_csv_contains_expected_header_row(self):
        response = self._authed_client().get(reverse('stocklevels-csv'))
        content = response.content.decode('utf-8')
        for header in ['Part Number', 'Part Description', 'Range Name', 'Stock Level']:
            self.assertIn(header, content)

    def test_csv_contains_data_rows(self):
        response = self._authed_client().get(reverse('stocklevels-csv'))
        content = response.content.decode('utf-8')
        self.assertIn('CSV001', content)
        self.assertIn('CSV Part', content)

    def test_csv_scoped_user_excludes_other_company_data(self):
        StockLevels.objects.create(
            company="OTHER", partNum="OTHER001", partDesc="Other Part",
            rangeName="RangeY", groupDesc="GroupY", subGroupDesc="SubY", stockLev=1
        )
        response = self._authed_client().get(reverse('stocklevels-csv'))
        content = response.content.decode('utf-8')
        self.assertNotIn('OTHER001', content)


# Test the registration view (enabled/disabled, form, redirects)
class RegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.site_settings = SiteSettings.load()

    def test_register_redirects_to_login_when_disabled(self):
        self.site_settings.registration_enabled = False
        self.site_settings.save()
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('login'), fetch_redirect_response=False)

    def test_register_page_loads_when_enabled(self):
        self.site_settings.registration_enabled = True
        self.site_settings.save()
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_successful_registration_creates_user(self):
        self.site_settings.registration_enabled = True
        self.site_settings.save()
        self.client.post(reverse('register'), {
            'username': 'brandnewuser',
            'email': 'brand@new.com',
            'company_Name': 'Brand New Co',
            'first_name': 'Brand',
            'last_name': 'New',
            'password': 'StrongPass1!',
            'password_confirm': 'StrongPass1!',
        })
        self.assertTrue(User.objects.filter(username='brandnewuser').exists())

    def test_successful_registration_creates_user_profile(self):
        self.site_settings.registration_enabled = True
        self.site_settings.save()
        self.client.post(reverse('register'), {
            'username': 'brandnewuser',
            'email': 'brand@new.com',
            'company_Name': 'Brand New Co',
            'first_name': 'Brand',
            'last_name': 'New',
            'password': 'StrongPass1!',
            'password_confirm': 'StrongPass1!',
        })
        user = User.objects.get(username='brandnewuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_successful_registration_redirects_to_profile(self):
        self.site_settings.registration_enabled = True
        self.site_settings.save()
        response = self.client.post(reverse('register'), {
            'username': 'brandnewuser',
            'email': 'brand@new.com',
            'company_Name': 'Brand New Co',
            'first_name': 'Brand',
            'last_name': 'New',
            'password': 'StrongPass1!',
            'password_confirm': 'StrongPass1!',
        })
        self.assertRedirects(response, reverse('profile'), fetch_redirect_response=False)

    def test_already_authenticated_user_is_redirected(self):
        self.site_settings.registration_enabled = True
        self.site_settings.save()
        existing = User.objects.create_user(username='existing', password='pass')
        self.client.force_login(existing)
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('profile'), fetch_redirect_response=False)

    def test_invalid_registration_form_stays_on_page(self):
        self.site_settings.registration_enabled = True
        self.site_settings.save()
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'not-an-email',
            'password': 'weak',
            'password_confirm': 'weak',
        })
        self.assertEqual(response.status_code, 200)


# Test the profile view (login required, update)
class ProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="profuser", password="pass")
        UserProfile.objects.create(user=self.user)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('profile')}",
            fetch_redirect_response=False,
        )

    def test_profile_accessible_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_update_saves_changes(self):
        self.client.force_login(self.user)
        self.client.post(reverse('profile'), {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name',
            'website': 'https://example.com',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')


# Run this module's tests when file is executed directly
if __name__ == '__main__':
    from django.test.utils import get_runner
    from django.conf import settings
    runner = get_runner(settings)(verbosity=2)
    failures = runner.run_tests(['api.tests.test_views'])
    sys.exit(1 if failures else 0)
