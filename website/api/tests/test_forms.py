# =============================================================================
# SeconiqueStockAPI | tests/test_forms.py
# =============================================================================
# Form tests: UserRegistrationForm validation.
# Run with: python manage.py test api.tests.test_forms
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
from api.forms import UserRegistrationForm

# Test the UserRegistrationForm validation
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


# Run this module's tests when file is executed directly
if __name__ == '__main__':
    from django.test.utils import get_runner
    from django.conf import settings
    runner = get_runner(settings)(verbosity=2)
    failures = runner.run_tests(['api.tests.test_forms'])
    sys.exit(1 if failures else 0)
