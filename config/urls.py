"""Root URL configuration: each app owns its own urls.py."""
from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import admin_dashboard

urlpatterns = [
    path("admin/", admin.site.urls),                      # Django admin (full CRUD)
    path("manage/", admin_dashboard, name="admin_dashboard"),  # staff statistics page
    path("accounts/", include("apps.accounts.urls")),
    path("favorites/", include("apps.favorites.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("", include("apps.submissions.urls")),            # /submit/, /contact/, /newsletter/
    path("", include("apps.tools.urls")),                  # home, explore, categories, details...
]

admin.site.site_header = "AI HUB administration"
admin.site.site_title = "AI HUB admin"
admin.site.index_title = "Manage tools, users and reviews"
