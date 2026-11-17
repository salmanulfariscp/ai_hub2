from django.contrib import admin, messages

from .models import Category, RecentlyViewed, Tool


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.action(description="Approve selected tools")
def approve_tools(modeladmin, request, queryset):
    updated = queryset.update(status=Tool.APPROVED)
    modeladmin.message_user(request, f"{updated} tool(s) approved.", messages.SUCCESS)


@admin.action(description="Feature selected tools")
def feature_tools(modeladmin, request, queryset):
    updated = queryset.update(is_featured=True)
    modeladmin.message_user(request, f"{updated} tool(s) featured.", messages.SUCCESS)


@admin.action(description="Remove featured flag")
def unfeature_tools(modeladmin, request, queryset):
    updated = queryset.update(is_featured=False)
    modeladmin.message_user(request, f"{updated} tool(s) un-featured.", messages.SUCCESS)


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "pricing_model", "status", "is_featured", "is_trending", "data_verified")
    list_filter = ("status", "category", "pricing_model", "is_featured", "is_trending", "is_open_source", "data_verified")
    list_editable = ("status", "is_featured", "is_trending")
    search_fields = ("name", "tagline", "description")
    prepopulated_fields = {"slug": ("name",)}
    actions = [approve_tools, feature_tools, unfeature_tools]
    fieldsets = (
        (None, {"fields": ("name", "slug", "tagline", "description", "category", "website_url")}),
        ("Pricing & platform", {"fields": ("pricing_model", "pricing_note", "is_open_source", "platforms")}),
        ("Profile content", {"fields": ("features", "pros", "cons", "use_cases")}),
        ("Publishing", {"fields": ("status", "is_featured", "is_trending", "data_verified", "added_by")}),
    )


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ("user", "tool", "viewed_at")
