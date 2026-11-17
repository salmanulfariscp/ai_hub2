from django.urls import path

from . import views

app_name = "submissions"

urlpatterns = [
    path("submit/", views.submit_tool, name="submit"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/", views.newsletter_signup, name="newsletter"),
]
