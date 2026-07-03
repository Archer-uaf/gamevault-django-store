from django.conf import settings
from django.urls import reverse


def test_project_apps_are_installed() -> None:
    expected_apps = {
        "products.apps.ProductsConfig",
        "orders.apps.OrdersConfig",
        "users.apps.UsersConfig",
        "reviews.apps.ReviewsConfig",
    }

    assert expected_apps.issubset(set(settings.INSTALLED_APPS))


def test_documentation_urls_are_configured() -> None:
    assert reverse("schema") == "/api/schema/"
    assert reverse("swagger-ui") == "/api/docs/"
