from django.contrib import admin

from stream.models import (
    Movie,
    MovieContent,
    UserMovieHistory,
    MovieSubtitle,
    MyList,
)


admin.site.register(Movie)
admin.site.register(MovieContent)
admin.site.register(UserMovieHistory)
admin.site.register(MovieSubtitle)
admin.site.register(MyList)
