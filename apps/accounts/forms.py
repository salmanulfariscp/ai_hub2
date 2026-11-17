from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)

from apps.common import BootstrapFormMixin

from .models import Profile

User = get_user_model()


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    """Django's UserCreationForm already validates and hashes the password for us."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class ResetRequestForm(BootstrapFormMixin, PasswordResetForm):
    pass


class NewPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass


class ChangePasswordForm(BootstrapFormMixin, PasswordChangeForm):
    pass


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Another account already uses this email.")
        return email


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("profession", "interests", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}
