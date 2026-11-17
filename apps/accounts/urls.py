from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import path, reverse_lazy

from . import views
from .forms import ChangePasswordForm, LoginForm, NewPasswordForm, ResetRequestForm

app_name = "accounts"

AUTH_TEMPLATE = "accounts/auth_form.html"
MESSAGE_TEMPLATE = "accounts/auth_message.html"


class PasswordChange(SuccessMessageMixin, auth_views.PasswordChangeView):
    success_message = "Your password was changed."


urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name=AUTH_TEMPLATE,
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
            extra_context={"page": "login", "title": "Welcome back",
                           "subtitle": "Log in to see your favourites, reviews and collections.", "button": "Log in"},
        ),
        name="login",
    ),
    # Logout must be a POST request (the navbar uses a small form)
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "password-change/",
        PasswordChange.as_view(
            template_name=AUTH_TEMPLATE,
            form_class=ChangePasswordForm,
            success_url=reverse_lazy("accounts:profile"),
            extra_context={"page": "change", "title": "Change password", "subtitle": "", "button": "Change password"},
        ),
        name="password_change",
    ),
    # --- Forgot password flow (4 built-in views). In development the email is printed in the terminal.
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name=AUTH_TEMPLATE,
            form_class=ResetRequestForm,
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
            extra_context={"page": "reset", "title": "Forgot your password?",
                           "subtitle": "Enter your email and we will send you a reset link.", "button": "Send reset link"},
        ),
        name="password_reset",
    ),
    path(
        "password-reset/sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name=MESSAGE_TEMPLATE,
            extra_context={"title": "Check your email", "icon": "bi-envelope-check",
                           "message": "If an account exists for that address, a reset link is on its way."},
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name=AUTH_TEMPLATE,
            form_class=NewPasswordForm,
            success_url=reverse_lazy("accounts:password_reset_complete"),
            extra_context={"page": "reset_confirm", "title": "Choose a new password", "subtitle": "", "button": "Save password"},
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name=MESSAGE_TEMPLATE,
            extra_context={"title": "Password changed", "icon": "bi-check-circle",
                           "message": "Your password has been updated. You can now log in.", "show_login": True},
        ),
        name="password_reset_complete",
    ),
]
