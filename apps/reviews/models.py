from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.tools.models import Tool


class Review(models.Model):
    """One user's rating + comment for one tool. Admins can hide it with is_approved."""

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=1500)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tool", "user")  # one review per user per tool
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tool} - {self.rating}/5 by {self.user}"
