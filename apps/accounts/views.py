from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import redirect, render

from apps.favorites.models import Collection, Favorite
from apps.reviews.models import Review
from apps.submissions.models import ContactMessage, NewsletterSubscriber, ToolSubmission
from apps.tools.models import Category, RecentlyViewed, Tool

from .forms import ProfileForm, RegisterForm, UserUpdateForm
from .models import Profile

User = get_user_model()


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)  # log the new user in straight away
        messages.success(request, "Welcome to AI HUB! Your account is ready.")
        return redirect("accounts:dashboard")
    return render(
        request,
        "accounts/auth_form.html",
        {"form": form, "page": "register", "title": "Create your account",
         "subtitle": "Save favourite tools, write reviews and build collections.", "button": "Create account"},
    )


@login_required
def profile(request):
    profile_obj, _created = Profile.objects.get_or_create(user=request.user)
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=profile_obj)
    if request.method == "POST":
        user_ok, profile_ok = user_form.is_valid(), profile_form.is_valid()
        if user_ok and profile_ok:
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    return render(request, "profile.html", {"user_form": user_form, "profile_form": profile_form})


@login_required
def dashboard(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user).select_related("tool__category")
    favourite_tools = [fav.tool for fav in favorites]

    # Simple "recommended": tools from categories the user already bookmarked
    category_ids = {tool.category_id for tool in favourite_tools}
    suggestions = Tool.objects.approved().select_related("category")
    if category_ids:
        suggestions = suggestions.filter(category_id__in=category_ids).exclude(favorited_by__user=user)
    else:
        suggestions = suggestions.filter(is_featured=True)

    context = {
        "favourite_tools": favourite_tools,
        "recent_tools": [v.tool for v in RecentlyViewed.objects.filter(user=user).select_related("tool__category")[:4]],
        "collections": Collection.objects.filter(user=user).annotate(tool_count=Count("tools")),
        "my_reviews": Review.objects.filter(user=user).select_related("tool"),
        "my_submissions": ToolSubmission.objects.filter(submitted_by=user),
        "suggestions": suggestions[:4],
    }
    return render(request, "dashboard.html", context)


@staff_member_required
def admin_dashboard(request):
    """Statistics page for staff. Add/edit/delete happens in Django admin (linked from here)."""
    top_favourited = (
        Tool.objects.approved().annotate(fav_count=Count("favorited_by")).filter(fav_count__gt=0).order_by("-fav_count")[:5]
    )
    context = {
        "stats": [
            ("Approved tools", Tool.objects.approved().count(), "bi-grid", "admin:tools_tool_changelist"),
            ("Categories", Category.objects.count(), "bi-collection", "admin:tools_category_changelist"),
            ("Users", User.objects.count(), "bi-people", "admin:auth_user_changelist"),
            ("Reviews", Review.objects.count(), "bi-chat-square-text", "admin:reviews_review_changelist"),
            ("Pending submissions", ToolSubmission.objects.filter(status=ToolSubmission.PENDING).count(),
             "bi-inbox", "admin:submissions_toolsubmission_changelist"),
            ("Contact messages", ContactMessage.objects.count(), "bi-envelope", "admin:submissions_contactmessage_changelist"),
            ("Newsletter sign-ups", NewsletterSubscriber.objects.count(), "bi-megaphone",
             "admin:submissions_newslettersubscriber_changelist"),
            ("Favourites saved", Favorite.objects.count(), "bi-heart", "admin:favorites_favorite_changelist"),
        ],
        "pending": ToolSubmission.objects.filter(status=ToolSubmission.PENDING)[:5],
        "top_favourited": top_favourited,
        "latest_reviews": Review.objects.select_related("tool", "user")[:5],
        "unverified_count": Tool.objects.filter(data_verified=False).count(),
    }
    return render(request, "admin_dashboard.html", context)
