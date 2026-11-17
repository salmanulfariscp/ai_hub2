"""Variables available in EVERY template (registered in settings.TEMPLATES)."""
from django.conf import settings

from apps.favorites.models import Favorite

from .models import Category


def site_context(request):
    favorite_slugs = []
    if request.user.is_authenticated:
        favorite_slugs = list(Favorite.objects.filter(user=request.user).values_list("tool__slug", flat=True))
    return {
        "SITE_NAME": "AI HUB",
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "nav_categories": Category.objects.all(),
        "favorite_slugs": favorite_slugs,
    }
