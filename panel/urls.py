from django.urls import path, include

from . import views

app_name: str = "panel"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", include("panel.api.urls"), name="panel_api"),
    path("add-movie/", views.add_movie, name="add_movie"),
    path("movie-detail/<int:movie_id>", views.movie_detail, name="movie_detail"),
    path(
        "background-management/",
        views.background_management,
        name="background_management",
    ),
    path("setup-panel/", views.setup_panel, name="setup_panel"),
    path(
        "background-processes/",
        views.background_processes,
        name="background_processes",
    ),
    path("history/", views.user_history, name="user_history"),
    path("settings/", views.settings, name="settings"),
    path("initial-setup/", views.initial_setup, name="initial_setup"),
    path("design/", include("panel.design_pages.urls"), name="design"),
]
