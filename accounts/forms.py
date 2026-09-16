import re
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.models import Profile, Role

User = get_user_model()


class StudentLoginForm(forms.Form):
    login_identifier = forms.CharField(
        label="Email Address or Student ID",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "bfa-auth-input",
                "placeholder": "Enter your email or student ID",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "bfa-auth-input",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "bfa-auth-checkbox"}),
    )


class StudentRegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        label="First Name *",
        widget=forms.TextInput(
            attrs={"class": "bfa-auth-input", "placeholder": "Enter your first name"}
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        label="Last Name *",
        widget=forms.TextInput(
            attrs={"class": "bfa-auth-input", "placeholder": "Enter your last name"}
        ),
    )
    email = forms.EmailField(
        label="Email Address *",
        widget=forms.EmailInput(
            attrs={"class": "bfa-auth-input", "placeholder": "Enter your email address"}
        ),
    )
    phone = forms.CharField(
        max_length=30,
        label="Phone Number *",
        widget=forms.TextInput(
            attrs={"class": "bfa-auth-input", "placeholder": "Enter your phone number"}
        ),
    )
    dob = forms.DateField(
        label="Date of Birth *",
        widget=forms.DateInput(attrs={"class": "bfa-auth-input", "type": "date"}),
    )
    password = forms.CharField(
        label="Password *",
        widget=forms.PasswordInput(
            attrs={
                "class": "bfa-auth-input",
                "placeholder": "Create a password (min. 10 chars)",
            }
        ),
    )
    confirm_password = forms.CharField(
        label="Confirm Password *",
        widget=forms.PasswordInput(
            attrs={"class": "bfa-auth-input", "placeholder": "Confirm your password"}
        ),
    )
    student_id = forms.CharField(
        required=False,
        label="Student ID (if available)",
        widget=forms.TextInput(
            attrs={"class": "bfa-auth-input", "placeholder": "Enter your student ID"}
        ),
    )
    agree_terms = forms.BooleanField(
        required=True,
        error_messages={
            "required": "You must agree to the Terms of Service and Privacy Policy."
        },
        widget=forms.CheckboxInput(attrs={"class": "bfa-auth-checkbox"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password or len(password) < 10:
            raise ValidationError("Password must be at least 10 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one digit.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        confirm_pw = cleaned_data.get("confirm_password")
        if pw and confirm_pw and pw != confirm_pw:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data
