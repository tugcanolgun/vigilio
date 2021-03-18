from rest_framework.exceptions import NotFound

from stream.api.serializers import SaveCurrentSecond
from stream.models import Movie


class SaveCurrentSecondValidator:
    @staticmethod
    def validate(save_current_second: SaveCurrentSecond):
        try:
            Movie.objects.get(id=save_current_second.movie_id)
        except Movie.DoesNotExist:
            raise NotFound(
                {
                    "error": f"Movie ID: {save_current_second.movie_id} could not be found."
                }
            )
