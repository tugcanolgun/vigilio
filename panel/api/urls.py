from django.urls import path, include

from . import views

urlpatterns = [
    path("t_status", views.TorrentEndpoint.as_view(), name="background_management"),
    path("celery", views.CeleryEndpoint.as_view(), name="celery_endpoint"),
    path(
        "movie-management",
        views.MovieManagementEndpoint.as_view(),
        name="movie_management",
    ),
    path("files", views.FilesEndpoint.as_view(), name="files"),
    path("add-movie", views.MovieAddEndpoint.as_view(), name="add_movie"),
    path(
        "global-settings",
        views.GlobalSettingsEndpoint.as_view(),
        name="global_settings",
    ),
    path("mud-sources", views.MudSourcesList.as_view(), name="mud_sources"),
    path(
        "mud-source/<int:mud_id>", views.MudSourceEndpoint.as_view(), name="mud_source"
    ),
    path(
        "redownload-subtitles",
        views.RedownloadSubtitlesEndpoint.as_view(),
        name="redownload_subtitles",
    ),
    path("user/", include("panel.api.user.urls"), name="panel_user"),
]
