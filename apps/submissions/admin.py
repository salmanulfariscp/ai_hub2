from django.contrib import admin, messages

from apps.common import unique_slug
from apps.tools.models import Tool

from .models import ContactMessage, NewsletterSubscriber, ToolSubmission


@admin.action(description="Approve selected submissions (publishes them as tools)")
def approve_submissions(modeladmin, request, queryset):
    approved = 0
    for submission in queryset.filter(status=ToolSubmission.PENDING):
        if submission.category is None:
            continue  # cannot publish without a category
        tool = Tool.objects.create(
            name=submission.tool_name,
            slug=unique_slug(Tool, submission.tool_name),
            tagline=submission.short_description,
            description=submission.description,
            category=submission.category,
            website_url=submission.website_url,
            pricing_model=submission.pricing_model,
            pricing_note="Submitted by a user - not verified yet. Check the official site.",
            features=submission.features,
            status=Tool.APPROVED,
            data_verified=False,
            added_by=submission.submitted_by,
        )
        submission.status = ToolSubmission.APPROVED
        submission.tool = tool
        submission.save()
        approved += 1
    modeladmin.message_user(request, f"{approved} submission(s) approved and published.", messages.SUCCESS)


@admin.action(description="Reject selected submissions")
def reject_submissions(modeladmin, request, queryset):
    count = queryset.filter(status=ToolSubmission.PENDING).update(status=ToolSubmission.REJECTED)
    modeladmin.message_user(request, f"{count} submission(s) rejected.", messages.SUCCESS)


@admin.register(ToolSubmission)
class ToolSubmissionAdmin(admin.ModelAdmin):
    list_display = ("tool_name", "category", "submitted_by", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("tool_name", "website_url", "contact_email")
    actions = [approve_submissions, reject_submissions]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_read", "created_at")
    list_filter = ("is_read",)
    list_editable = ("is_read",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
