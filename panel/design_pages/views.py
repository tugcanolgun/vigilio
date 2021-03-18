from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render


@login_required
def index(request: WSGIRequest) -> HttpResponse:
    return render(request, "design/index.html")
