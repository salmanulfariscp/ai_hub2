from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from apps.favorites.models import Collection, Favorite
from apps.reviews.forms import ReviewForm
from apps.reviews.models import Review

from .forms import RecommendationForm
from .models import Category, RecentlyViewed, Tool
from .recommender import BUDGETS, PROFESSIONS, PURPOSES, recommend_tools


def home(request):
    """Homepage: every section is a small database query."""
    approved = Tool.objects.approved().select_related("category")

    # "Recommended": personal picks for logged-in users who have favourites, otherwise featured tools.
    recommended, recommended_title = None, "Recommended to start with"
    if request.user.is_authenticated:
        favourite_category_ids = Favorite.objects.filter(user=request.user).values_list("tool__category_id", flat=True)
        recommended = (
            approved.filter(category_id__in=list(favourite_category_ids))
            .exclude(favorited_by__user=request.user)[:4]
        )
        if recommended:
            recommended_title = "Recommended for you"
    if not recommended:
        recommended = approved.filter(is_featured=True).order_by("-id")[:4]

    context = {
        "categories": Category.objects.annotate(tool_count=Count("tools", filter=Q(tools__status=Tool.APPROVED))),
        "popular": approved.annotate(favorite_count=Count("favorited_by", distinct=True)).order_by(
            "-favorite_count", "-is_featured", "name"
        )[:4],
        "featured": approved.filter(is_featured=True)[:4],
        "trending": approved.filter(is_trending=True)[:4],
        "recent": approved.order_by("-created_at", "-id")[:4],
        "free_tools": approved.filter(pricing_model__in=[Tool.FREE, Tool.FREEMIUM]).order_by("pricing_model", "name")[:4],
        "recommended": recommended,
        "recommended_title": recommended_title,
        "tool_total": approved.count(),
    }
    return render(request, "index.html", context)


def explore(request):
    """The tool directory. Filtering/sorting/pagination run in JavaScript (static/js/search.js)."""
    return render(request, "explore.html", {"categories": Category.objects.all(), "active_category": None})


def categories(request):
    items = Category.objects.annotate(tool_count=Count("tools", filter=Q(tools__status=Tool.APPROVED)))
    return render(request, "categories.html", {"categories": items})


def category_detail(request, slug):
    """Same explorer page, locked to one category."""
    category = get_object_or_404(Category, slug=slug)
    return render(request, "explore.html", {"categories": Category.objects.all(), "active_category": category})


def tool_detail(request, slug):
    tool = get_object_or_404(Tool.objects.approved().select_related("category"), slug=slug)

    # Remember this visit for logged-in users (guests use localStorage in main.js)
    if request.user.is_authenticated:
        visit, created = RecentlyViewed.objects.get_or_create(user=request.user, tool=tool)
        if not created:
            visit.save()  # auto_now refreshes viewed_at

    reviews = tool.reviews.filter(is_approved=True).select_related("user")
    rating_stats = Tool.objects.filter(pk=tool.pk).with_stats().values("avg_rating", "review_count").first()
    user_review, collections = None, []
    if request.user.is_authenticated:
        user_review = Review.objects.filter(tool=tool, user=request.user).first()
        collections = Collection.objects.filter(user=request.user)

    context = {
        "tool": tool,
        "similar_tools": Tool.objects.approved().select_related("category")
        .filter(category=tool.category).exclude(pk=tool.pk)[:3],
        "reviews": reviews,
        "avg_rating": rating_stats["avg_rating"],
        "review_count": rating_stats["review_count"],
        "review_form": ReviewForm(instance=user_review),
        "user_review": user_review,
        "collections": collections,
    }
    return render(request, "tool-details.html", context)


def compare(request):
    """Selection and the comparison table are built in static/js/compare.js."""
    return render(request, "compare.html")


def recommendations(request):
    """Quiz page. With answers in the URL (?purpose=...) it also shows ranked results."""
    results, answers = [], None
    if request.GET.get("purpose"):
        form = RecommendationForm(request.GET)
        if form.is_valid():
            answers = form.cleaned_data
            tools = Tool.objects.approved().select_related("category")
            results = recommend_tools(list(tools), answers, limit=6)
    context = {
        "purposes": PURPOSES,
        "professions": PROFESSIONS,
        "budgets": BUDGETS,
        "categories": Category.objects.all(),
        "answers": answers,
        "results": results,
    }
    return render(request, "recommendations.html", context)


def about(request):
    return render(request, "about.html", {"tool_total": Tool.objects.approved().count()})


@require_GET
def api_tools(request):
    """JSON list of every approved tool. The JavaScript files filter and sort this list."""
    tools = Tool.objects.approved().select_related("category").with_stats()
    data = []
    for tool in tools:
        data.append(
            {
                "slug": tool.slug,
                "name": tool.name,
                "tagline": tool.tagline,
                "url": tool.get_absolute_url(),
                "website": tool.website_url,
                "domain": tool.domain,
                "category": tool.category.name,
                "category_slug": tool.category.slug,
                "category_order": tool.category.order,
                "pricing": tool.pricing_model,
                "pricing_label": tool.get_pricing_model_display(),
                "free_plan": tool.has_free_plan,
                "open_source": tool.is_open_source,
                "featured": tool.is_featured,
                "trending": tool.is_trending,
                "platforms": tool.platforms_list(),
                "features": tool.features_list(),
                "pros": tool.pros_list(),
                "cons": tool.cons_list(),
                "use_cases": tool.use_cases_list(),
                "rating": round(tool.avg_rating, 1) if tool.avg_rating else None,
                "review_count": tool.review_count,
                "added": tool.created_at.isoformat(),
            }
        )
    return JsonResponse({"tools": data})
