from django.conf import settings
from django.db import models

from apps.tools.models import Tool


class Favorite(models.Model):
    """A bookmark: links one user to one tool (a many-to-many relation with its own table)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tool")  # a user cannot bookmark the same tool twice
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.tool}"


class Collection(models.Model):
    """A named list of tools that belongs to one user, e.g. 'My coding stack'."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="collections")
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    tools = models.ManyToManyField(Tool, blank=True, related_name="collections")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name
