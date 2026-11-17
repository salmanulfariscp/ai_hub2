from django.urls import path

from . import views

app_name = "tools"

urlpatterns = [
    path("", views.home, name="home"),
    path("explore/", views.explore, name="explore"),
    path("categories/", views.categories, name="categories"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("tools/<slug:slug>/", views.tool_detail, name="detail"),
    path("compare/", views.compare, name="compare"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("about/", views.about, name="about"),
    path("api/tools/", views.api_tools, name="api_tools"),
]
