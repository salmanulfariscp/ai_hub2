from django.contrib import admin

from .models import Collection, Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "tool", "created_at")
    search_fields = ("user__username", "tool__name")


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    filter_horizontal = ("tools",)
    search_fields = ("name", "user__username")
