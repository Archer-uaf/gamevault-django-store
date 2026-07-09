from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_uses_expected_template(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertContains(response, "GameVault")

    def test_popular_genre_links_point_to_filtered_catalog(self) -> None:
        response = self.client.get("/")

        for slug in (
            "action",
            "rpg",
            "adventure",
            "horror",
            "strategy",
            "racing",
            "indie",
            "simulation",
        ):
            self.assertContains(
                response,
                f'{reverse("products:product_list")}?category={slug}',
            )
        self.assertNotContains(response, 'href="#"')

    def test_recommended_game_cards_link_to_product_detail(self) -> None:
        response = self.client.get("/")

        for slug in (
            "cyberpunk-2077",
            "the-witcher-3-wild-hunt",
            "elden-ring",
        ):
            self.assertContains(
                response,
                reverse("products:product_detail", kwargs={"slug": slug}),
            )
