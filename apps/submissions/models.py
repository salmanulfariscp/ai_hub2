from django.conf import settings
from django.db import models

from apps.tools.models import Category, Tool


class ToolSubmission(models.Model):
    """A tool suggested by a visitor. An admin reviews it, then approves (creates a Tool) or rejects."""

    PENDING, APPROVED, REJECTED = "pending", "approved", "rejected"
    STATUS_CHOICES = [(PENDING, "Pending"), (APPROVED, "Approved"), (REJECTED, "Rejected")]

    tool_name = models.CharField(max_length=100)
    website_url = models.URLField()
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name="submissions")
    pricing_model = models.CharField(max_length=10, choices=Tool.PRICING_CHOICES, default=Tool.FREEMIUM)
    short_description = models.CharField(max_length=160)
    description = models.TextField()
    features = models.TextField(blank=True, help_text="One per line")
    contact_email = models.EmailField()
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="submissions"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    admin_notes = models.TextField(blank=True)
    tool = models.ForeignKey(Tool, null=True, blank=True, on_delete=models.SET_NULL, related_name="source_submissions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tool_name} ({self.status})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField(max_length=3000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.email}"


class NewsletterSubscriber(models.Model):
    """Only stores the address. This project does not send newsletters by itself."""

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
