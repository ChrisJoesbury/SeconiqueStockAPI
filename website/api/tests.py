# =============================================================================
# SeconiqueStockAPI | tests.py
# =============================================================================
# Test suite covering models, forms, authentication, serializers, and all API
# and view endpoints. Runs against an in-memory SQLite database with no external
# dependencies. Execute with: python manage.py test api
# =============================================================================

#Get Django files
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse

#Get Framework files
from rest_framework.test import APIClient
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_api_key.models import APIKey

#Get Local files
from api.models import StockLevels, UserProfile, SiteSettings
from api.forms import UserRegistrationForm
from api.authentication import CustomAPIKeyAuthentication
from api.serializers import StockLevelsSerializer


# ── Model Tests ───────────────────────────────────────────────────────────────

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


# ── Form Tests ────────────────────────────────────────────────────────────────

class UserRegistrationFormTest(TestCase):

    def _valid_data(self, **overrides):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'company_Name': 'Acme Ltd',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'StrongPass1!',
            'password_confirm': 'StrongPass1!',
        }
        data.update(overrides)
        return data

    def test_valid_form_is_valid(self):
        form = UserRegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_too_short_is_invalid(self):
        form = UserRegistrationForm(data=self._valid_data(password='Short1!', password_confirm='Short1!'))
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_password_no_uppercase_is_invalid(self):
        form = UserRegistrationForm(data=self._valid_data(password='alllowercase1!', password_confirm='alllowercase1!'))
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_password_no_digit_is_invalid(self):
        form = UserRegistrationForm(data=self._valid_data(password='NoDigitPass!!', password_confirm='NoDigitPass!!'))
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_password_no_special_character_is_invalid(self):
        form = UserRegistrationForm(data=self._valid_data(password='NoSpecialChar1', password_confirm='NoSpecialChar1'))
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_mismatched_passwords_are_invalid(self):
        form = UserRegistrationForm(data=self._valid_data(password_confirm='DifferentPass1!'))
        self.assertFalse(form.is_valid())

    def test_duplicate_username_is_invalid(self):
        User.objects.create_user(username='newuser', password='anything')
        form = UserRegistrationForm(data=self._valid_data())
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_duplicate_email_is_invalid(self):
        User.objects.create_user(username='other', email='new@example.com', password='anything')
        form = UserRegistrationForm(data=self._valid_data())
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_all_required_fields_enforced(self):
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        for field in ['username', 'email', 'company_Name', 'first_name', 'last_name', 'password', 'password_confirm']:
            self.assertIn(field, form.errors)


# ── Authentication Tests ──────────────────────────────────────────────────────

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


# ── Serializer Tests ──────────────────────────────────────────────────────────

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


# ── View Tests ────────────────────────────────────────────────────────────────

class HomeViewTest(TestCase):

    def test_home_redirects_to_api_docs(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/api/docs/', fetch_redirect_response=False)


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
