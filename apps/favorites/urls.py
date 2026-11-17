from django.urls import path

from . import views

app_name = "favorites"

urlpatterns = [
    path("", views.favorites_page, name="list"),
    path("toggle/", views.toggle_favorite, name="toggle"),
    path("sync/", views.sync_favorites, name="sync"),
    path("collections/create/", views.collection_create, name="collection_create"),
    path("collections/add/", views.collection_add, name="collection_add"),
    path("collections/<int:pk>/", views.collection_detail, name="collection_detail"),
    path("collections/<int:pk>/remove/", views.collection_remove, name="collection_remove"),
    path("collections/<int:pk>/delete/", views.collection_delete, name="collection_delete"),
]
