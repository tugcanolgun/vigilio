from django.urls import reverse


def _get_relative_path_to_watch(pk: int = 1) -> str:
    url: str = reverse("stream:watch", kwargs={"movie_id": pk})
    return url.replace(str(pk), "")
