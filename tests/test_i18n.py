import pytest
from django.test import Client
from django.urls import reverse


def test_home_page_uses_ukrainian_by_default(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    content = response.content.decode()

    assert '<html lang="uk">' in content
    assert "Головна" in content
    assert "Ігри" in content
    assert "Кошик" in content


def test_home_page_can_be_rendered_in_english(client: Client) -> None:
    response = client.get("/", HTTP_ACCEPT_LANGUAGE="en")

    assert response.status_code == 200
    content = response.content.decode()

    assert '<html lang="en">' in content
    assert "Home" in content
    assert "Games" in content
    assert "Cart" in content
    assert "Your next story starts here" in content
    assert "Featured games" in content
    assert "Footer navigation" in content


@pytest.mark.django_db
def test_catalog_page_can_be_rendered_in_english(client: Client) -> None:
    response = client.get(
        reverse("products:product_list"),
        HTTP_ACCEPT_LANGUAGE="en",
    )

    assert response.status_code == 200
    content = response.content.decode()

    assert '<html lang="en">' in content
    assert "Game catalog" in content
    assert "Filters" in content
    assert "Newest first" in content
    assert "No games found" in content


def test_language_switcher_is_visible(client: Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    content = response.content.decode()

    assert 'name="language"' in content
    assert 'value="uk"' in content
    assert 'value="en"' in content
    assert "UA" in content
    assert "EN" in content
