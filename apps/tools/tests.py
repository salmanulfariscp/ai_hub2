"""
Django tests. Run them with:  python manage.py test
(Written for learning - they cover pages, the JSON API, favourites, registration and the review rules.)
"""
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.favorites.models import Favorite
from apps.reviews.models import Review
from apps.tools.models import Category, Tool

User = get_user_model()


class BaseData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="AI Chatbots", slug="ai-chatbots", order=1)
        cls.tool = Tool.objects.create(
            name="Demo Bot", slug="demo-bot", tagline="A demo", description="Demo tool",
            category=cls.category, website_url="https://example.com", pricing_model="free",
        )
        cls.hidden = Tool.objects.create(
            name="Hidden", slug="hidden", tagline="x", description="x", category=cls.category,
            website_url="https://hidden.example.com", status=Tool.PENDING,
        )
        cls.user = User.objects.create_user("tester", "t@example.com", "S3cure-pass-123")


class PageTests(BaseData):
    def test_public_pages_load(self):
        for name in ["tools:home", "tools:explore", "tools:categories", "tools:compare", "tools:recommendations",
                     "tools:about", "favorites:list", "submissions:contact", "accounts:login", "accounts:register"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_detail_and_category(self):
        self.assertEqual(self.client.get(self.tool.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(self.category.get_absolute_url()).status_code, 200)

    def test_pending_tool_is_not_public(self):
        self.assertEqual(self.client.get(self.hidden.get_absolute_url()).status_code, 404)

    def test_api_lists_only_approved_tools(self):
        data = self.client.get(reverse("tools:api_tools")).json()
        self.assertEqual([t["slug"] for t in data["tools"]], ["demo-bot"])

    def test_recommendations_with_answers(self):
        url = reverse("tools:recommendations") + "?purpose=chat&profession=other&budget=free&prefer_free=yes"
        self.assertContains(self.client.get(url), "Demo Bot")

    def test_dashboard_requires_login(self):
        self.assertEqual(self.client.get(reverse("accounts:dashboard")).status_code, 302)


class FavoriteTests(BaseData):
    def post_toggle(self):
        return self.client.post(reverse("favorites:toggle"), json.dumps({"slug": "demo-bot"}), content_type="application/json")

    def test_guest_gets_401(self):
        self.assertEqual(self.post_toggle().status_code, 401)

    def test_toggle_adds_then_removes(self):
        self.client.login(username="tester", password="S3cure-pass-123")
        self.assertTrue(self.post_toggle().json()["favorited"])
        self.assertEqual(Favorite.objects.count(), 1)
        self.assertFalse(self.post_toggle().json()["favorited"])
        self.assertEqual(Favorite.objects.count(), 0)


class AccountTests(BaseData):
    def test_registration_creates_user_and_profile(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newuser", "email": "new@example.com", "password1": "Another-Str0ng-pass", "password2": "Another-Str0ng-pass",
        })
        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertTrue(User.objects.get(username="newuser").profile)

    def test_duplicate_email_rejected(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "other", "email": "T@example.com", "password1": "Another-Str0ng-pass", "password2": "Another-Str0ng-pass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="other").exists())


class ReviewTests(BaseData):
    def test_one_review_per_user_is_updated(self):
        self.client.login(username="tester", password="S3cure-pass-123")
        url = reverse("reviews:submit", args=["demo-bot"])
        self.client.post(url, {"rating": 4, "title": "Good", "body": "Useful for drafting."})
        self.client.post(url, {"rating": 5, "title": "Great", "body": "Even better now."})
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().rating, 5)
