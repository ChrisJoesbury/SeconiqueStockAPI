# =============================================================================
# SeconiqueStockAPI | forms.py
# =============================================================================
# Django forms for user account management. Includes UserUpdateForm (email/name),
# UserProfileUpdateForm (website URL), and UserRegistrationForm with full password
# complexity validation (12+ chars, uppercase, digit, special character).
# =============================================================================

#Get String library for password validation
import string

#Get Django files
from django import forms
from django.contrib.auth.models import User

#Get Local files
from api.models import UserProfile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Enter email'}),
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Last name'}),
        }


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['website']
        widgets = {
            'website': forms.URLInput(attrs={'class': 'input', 'placeholder': 'https://example.com'}),
        }


class UserRegistrationForm(forms.Form):
    """Registration form with password complexity validation."""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Enter username',
            'autocomplete': 'username',
            'required': True
        }),
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'placeholder': 'Enter email address',
            'autocomplete': 'email',
            'required': True
        })
    )
    company_Name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Enter company name',
            'autocomplete': 'organization',
            'required': True
        }),
        label="Company Name"
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Enter first name',
            'autocomplete': 'given-name',
            'required': True
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Enter last name',
            'autocomplete': 'family-name',
            'required': True
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
            'required': True
        }),
        help_text="Your password must contain at least 12 characters, one capital letter, one number, and one special character."
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
            'required': True
        }),
        label="Confirm Password"
    )

    def clean_username(self):
        """Validate that the chosen username is not already taken.

        Returns:
            str: The validated username value from cleaned_data.

        Raises:
            forms.ValidationError: If a User with the given username already exists.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        """Validate that the email address is not already registered.

        Returns:
            str: The validated email value from cleaned_data.

        Raises:
            forms.ValidationError: If a User with the given email already exists.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean_password(self):
        """Validate password complexity rules.

        Returns:
            str: The validated password value from cleaned_data.

        Raises:
            forms.ValidationError: If the password is shorter than 12 characters,
                lacks an uppercase letter, lacks a digit, or lacks a special character.

        Contract:
            Validation is skipped if password is empty or None (field-level
            required=True handles the missing-value case separately).
        """
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 12:
                raise forms.ValidationError("Password must be at least 12 characters long.")
            if not any(c.isupper() for c in password):
                raise forms.ValidationError("Password must contain at least one capital letter.")
            if not any(c.isdigit() for c in password):
                raise forms.ValidationError("Password must contain at least one number.")
            if not any(c in string.punctuation for c in password):
                raise forms.ValidationError("Password must contain at least one special character.")
        return password

    def clean(self):
        """Cross-field validation: ensure password and confirmation match.

        Returns:
            dict: The full cleaned_data dictionary.

        Raises:
            forms.ValidationError: If both password fields are present but their
                values do not match. The error is attached to the form (non-field)
                rather than to a specific field.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data
