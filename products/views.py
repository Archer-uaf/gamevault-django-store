"""Public pages related to the product catalog."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Render the static GameVault landing page."""
    return render(request, "pages/home.html")
