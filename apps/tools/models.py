"""
Core catalogue models.

Relationships (read this to understand the database):

    Category 1 ───< Tool          one category has many tools (Tool.category is a ForeignKey)
    Tool     1 ───< Review        (defined in apps/reviews)
    User     >───< Tool           through Favorite (apps/favorites): a many-to-many "bookmark"
    User     1 ───< RecentlyViewed >─── 1 Tool
"""
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.db.models import Avg, Count, Q
from django.urls import reverse

from apps.common import unique_slug


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="bi-cpu", help_text="Bootstrap Icons class, e.g. bi-image")
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first")

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tools:category", args=[self.slug])


class ToolQuerySet(models.QuerySet):
    """Reusable query helpers: Tool.objects.approved().with_stats()"""

    def approved(self):
        return self.filter(status=Tool.APPROVED)

    def with_stats(self):
        """Adds avg_rating and review_count (only approved reviews are counted)."""
        return self.annotate(
            avg_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
            review_count=Count("reviews", filter=Q(reviews__is_approved=True), distinct=True),
        )


def _lines(text):
    """Turn a multi-line text field into a clean list (one item per line)."""
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


class Tool(models.Model):
    FREE, FREEMIUM, PAID = "free", "freemium", "paid"
    PRICING_CHOICES = [(FREE, "Free"), (FREEMIUM, "Freemium"), (PAID, "Paid")]

    PENDING, APPROVED, REJECTED = "pending", "approved", "rejected"
    STATUS_CHOICES = [(PENDING, "Pending review"), (APPROVED, "Approved"), (REJECTED, "Rejected")]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=140, unique=True)
    tagline = models.CharField(max_length=160, help_text="One short sentence shown on cards")
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="tools")
    website_url = models.URLField(help_text="Official website")
    pricing_model = models.CharField(max_length=10, choices=PRICING_CHOICES, default=FREEMIUM)
    pricing_note = models.CharField(max_length=200, blank=True, help_text="General note only - never invent prices")
    is_open_source = models.BooleanField(default=False)
    platforms = models.CharField(max_length=200, blank=True, help_text="Comma separated, e.g. Web, iOS, Android")
    features = models.TextField(blank=True, help_text="One feature per line")
    pros = models.TextField(blank=True, help_text="One per line")
    cons = models.TextField(blank=True, help_text="One per line")
    use_cases = models.TextField(blank=True, help_text="One per line")
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False, help_text="Editorial flag set by admins")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=APPROVED)
    data_verified = models.BooleanField(
        default=False, help_text="Tick once an admin has checked this entry against the official site"
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="added_tools"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ToolQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Tool, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tools:detail", args=[self.slug])

    @property
    def domain(self):
        """Website host without 'www.' - used to fetch the tool's favicon."""
        host = urlparse(self.website_url).netloc
        return host[4:] if host.startswith("www.") else host

    @property
    def has_free_plan(self):
        return self.pricing_model in (self.FREE, self.FREEMIUM)

    def features_list(self):
        return _lines(self.features)

    def pros_list(self):
        return _lines(self.pros)

    def cons_list(self):
        return _lines(self.cons)

    def use_cases_list(self):
        return _lines(self.use_cases)

    def platforms_list(self):
        return [p.strip() for p in self.platforms.split(",") if p.strip()]


class RecentlyViewed(models.Model):
    """Remembers which tools a logged-in user opened (shown on the dashboard)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recently_viewed")
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="recent_views")
    viewed_at = models.DateTimeField(auto_now=True)  # refreshed every time .save() is called

    class Meta:
        unique_together = ("user", "tool")
        ordering = ["-viewed_at"]
        verbose_name_plural = "recently viewed"

    def __str__(self):
        return f"{self.user} viewed {self.tool}"
