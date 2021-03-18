from django.urls import path

from . import views

urlpatterns = [
    path(
        "change-password",
        views.ChangePasswordEndpoint.as_view(),
        name="change_password",
    ),
]
