from django.test import TestCase


class HomePageTests(TestCase):
    def test_home_page_uses_expected_template(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertContains(response, "GameVault")
