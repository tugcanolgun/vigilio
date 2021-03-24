from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render

from panel.decorators import demo_or_login_required


@demo_or_login_required
def index(request: WSGIRequest) -> HttpResponse:
    return render(request, "design/index.html")
