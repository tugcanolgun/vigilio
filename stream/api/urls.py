from django.urls import path

from . import views

urlpatterns = [
    path(
        "movies",
        views.MoviesEndpoint.as_view(),
        name="movies_api",
    ),
    path(
        "save-current-second",
        views.SaveCurrentSecondEndpoint.as_view(),
        name="save_current_second",
    ),
    path(
        "continue-movie-list",
        views.ContinueMoviesEndpoint.as_view(),
        name="continue_movie_list",
    ),
    path(
        "categories",
        views.CategoriesEndpoint.as_view(),
        name="categories_api",
    ),
]
