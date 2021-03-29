from django.db import models

from stream.models import MovieContent


class CoreModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class MovieTorrent(CoreModel):
    source = models.TextField()
    name = models.CharField(max_length=255)
    movie_content = models.ForeignKey(
        MovieContent, on_delete=models.SET_NULL, null=True
    )
    is_complete = models.BooleanField(default=False)


class MudSource(CoreModel):
    name = models.CharField(max_length=50)
    source = models.TextField()
    order = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["order", "updated_at"]
