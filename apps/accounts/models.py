from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extra information about a user. One User has exactly one Profile (OneToOne)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    profession = models.CharField(max_length=100, blank=True)
    interests = models.CharField(max_length=200, blank=True, help_text="e.g. coding, design, study")
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"Profile of {self.user}"
