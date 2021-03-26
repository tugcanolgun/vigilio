import logging
from typing import Dict

from django.contrib.auth.models import User
from rest_framework.exceptions import APIException

from stream.api.serializers import SaveCurrentSecond
from stream.models import UserMovieHistory, Movie

logger = logging.getLogger(__name__)


class SaveCurrentSecondHandler:
    def handle(
        self, save_current_second: SaveCurrentSecond, user: User
    ) -> Dict[str, bool]:
        is_watched: bool = self.check_is_watched(
            save_current_second=save_current_second
        )

        self.save_regular_user(
            save_current_second=save_current_second, user=user, is_watched=is_watched
        )

        return {"saveCurrentSecond": True}

    @staticmethod
    def save_regular_user(
        save_current_second: SaveCurrentSecond, user: User, is_watched: bool
    ) -> None:
        try:
            user_history: UserMovieHistory = UserMovieHistory.objects.get(
                user=user, movie=Movie.objects.get(id=save_current_second.movie_id)
            )
        except UserMovieHistory.DoesNotExist:
            user_history: UserMovieHistory = UserMovieHistory.objects.create(
                user=user, movie=Movie.objects.get(id=save_current_second.movie_id)
            )
        except UserMovieHistory.MultipleObjectsReturned:
            logger.exception(
                f"Multiple user movie history for user: {user.id} movie: {save_current_second.movie_id}"
            )
            raise APIException(
                f"Multiple user movie history for user: {user.id} movie: {save_current_second.movie_id}"
            )

        user_history.current_second = save_current_second.current_second
        user_history.remaining_seconds = save_current_second.remaining_seconds
        user_history.is_watched = is_watched
        user_history.save()

    @staticmethod
    def check_is_watched(save_current_second: SaveCurrentSecond) -> bool:
        if save_current_second.current_second == 0:
            return False
        # User history only keeps tract continue movie feature.
        # When implementing true history feature, adjust this.
        ratio: float = 0.9
        total: int = (
            save_current_second.current_second + save_current_second.remaining_seconds
        )
        if total < 360.0:
            ratio = 0.6

        if (save_current_second.current_second / total) > ratio:
            return True

        return False
