from django.urls import path, include

from . import views

app_name: str = "stream"

urlpatterns = [
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("api/", include("stream.api.urls"), name="stream_api"),
    path("watch/<int:movie_id>", views.watch, name="watch"),
    path("search", views.search, name="search"),
]
