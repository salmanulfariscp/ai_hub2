import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.tools.models import Tool

from .models import Collection, Favorite


def _read_json(request):
    """Safely read a JSON request body; always returns a dict."""
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def favorites_page(request):
    """Cards are drawn by static/js/favorites.js (localStorage for guests, database for members)."""
    return render(request, "favorites.html")


@require_POST
def toggle_favorite(request):
    """AJAX: add the tool to the user's favourites, or remove it if it is already there."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    tool = Tool.objects.approved().filter(slug=str(_read_json(request).get("slug", ""))).first()
    if tool is None:
        return JsonResponse({"error": "not_found"}, status=404)
    favourite, created = Favorite.objects.get_or_create(user=request.user, tool=tool)
    if not created:
        favourite.delete()
    return JsonResponse({"favorited": created})


@require_POST
def sync_favorites(request):
    """AJAX: copy bookmarks a guest saved in localStorage into the database after login."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)
    slugs = _read_json(request).get("slugs", [])
    if isinstance(slugs, list):
        for tool in Tool.objects.approved().filter(slug__in=[s for s in slugs[:200] if isinstance(s, str)]):
            Favorite.objects.get_or_create(user=request.user, tool=tool)
    all_slugs = list(Favorite.objects.filter(user=request.user).values_list("tool__slug", flat=True))
    return JsonResponse({"slugs": all_slugs})


# ------------------------------------------------------------ collections
@login_required
@require_POST
def collection_create(request):
    name = request.POST.get("name", "").strip()[:80]
    if not name:
        messages.error(request, "Give your collection a name.")
    elif Collection.objects.filter(user=request.user, name__iexact=name).exists():
        messages.error(request, "You already have a collection with that name.")
    else:
        Collection.objects.create(user=request.user, name=name, description=request.POST.get("description", "").strip()[:200])
        messages.success(request, f"Collection '{name}' created.")
    return redirect("accounts:dashboard")


@login_required
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    return render(request, "collection_detail.html", {
        "collection": collection,
        "tools": collection.tools.select_related("category"),
    })


@login_required
@require_POST
def collection_add(request):
    collection = get_object_or_404(Collection, pk=request.POST.get("collection_id") or 0, user=request.user)
    tool = get_object_or_404(Tool.objects.approved(), slug=request.POST.get("slug", ""))
    collection.tools.add(tool)
    messages.success(request, f"Added {tool.name} to {collection.name}.")
    return redirect(tool.get_absolute_url())


@login_required
@require_POST
def collection_remove(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    tool = get_object_or_404(Tool, slug=request.POST.get("slug", ""))
    collection.tools.remove(tool)
    messages.success(request, f"Removed {tool.name} from {collection.name}.")
    return redirect("favorites:collection_detail", pk=collection.pk)


@login_required
@require_POST
def collection_delete(request, pk):
    collection = get_object_or_404(Collection, pk=pk, user=request.user)
    collection.delete()
    messages.success(request, "Collection deleted.")
    return redirect("accounts:dashboard")
