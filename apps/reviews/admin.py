from django.contrib import admin, messages

from .models import Review


@admin.action(description="Hide selected reviews")
def hide_reviews(modeladmin, request, queryset):
    modeladmin.message_user(request, f"{queryset.update(is_approved=False)} review(s) hidden.", messages.SUCCESS)


@admin.action(description="Show selected reviews")
def show_reviews(modeladmin, request, queryset):
    modeladmin.message_user(request, f"{queryset.update(is_approved=True)} review(s) shown.", messages.SUCCESS)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("tool", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    list_editable = ("is_approved",)
    search_fields = ("tool__name", "user__username", "title", "body")
    actions = [hide_reviews, show_reviews]
