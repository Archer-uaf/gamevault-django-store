from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from products.models import Category, Product
from reviews.models import Review


class VerifiedPurchaseReviewTests(TestCase):
    product: Product
    user: Any

    @classmethod
    def setUpTestData(cls) -> None:
        category = Category.objects.create(name="Action", slug="reviews-action")
        cls.product = Product.objects.create(
            name="Review Test Game",
            slug="review-test-game",
            description="A game used by review flow tests.",
            price=Decimal("100.00"),
            category=category,
            platform=Product.Platform.PC,
            stock=10,
            is_active=True,
        )
        cls.user = get_user_model().objects.create_user(
            username="verified-player",
            password="StrongPassword123!",
        )

    def test_anonymous_user_does_not_see_active_review_form(self) -> None:
        response = self.client.get(self.product.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'class="review-form"')
        self.assertContains(
            response,
            "Увійдіть, щоб залишити відгук після покупки гри.",
        )

    def test_anonymous_review_post_redirects_to_login(self) -> None:
        response = self.client.post(
            self.product.get_absolute_url(),
            {"rating": "5", "comment": "Чудова гра."},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.headers["Location"].startswith(reverse("account:login"))
        )
        self.assertFalse(Review.objects.exists())

    def test_user_without_purchase_cannot_review(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(
            self.product.get_absolute_url(),
            {"rating": "5", "comment": "Чудова гра."},
            follow=True,
        )

        self.assertFalse(Review.objects.exists())
        self.assertContains(
            response,
            "Залишити відгук можна лише після покупки цієї гри.",
        )

    def test_user_with_cancelled_order_cannot_review(self) -> None:
        order = self.create_purchase(user=self.user)
        order.status = Order.Status.CANCELLED
        order.save(update_fields=("status",))
        self.client.force_login(self.user)

        self.client.post(
            self.product.get_absolute_url(),
            {"rating": "5", "comment": "Скасоване замовлення."},
        )

        self.assertFalse(Review.objects.exists())

    def test_guest_purchase_does_not_allow_review(self) -> None:
        self.create_purchase(user=None)
        self.client.force_login(self.user)

        self.client.post(
            self.product.get_absolute_url(),
            {"rating": "5", "comment": "Гостьове замовлення."},
        )

        self.assertFalse(Review.objects.exists())

    def test_user_with_purchase_can_see_review_form(self) -> None:
        self.create_purchase(user=self.user)
        self.client.force_login(self.user)

        response = self.client.get(self.product.get_absolute_url())

        self.assertContains(response, 'class="review-form"')
        self.assertContains(response, "Залишити відгук")

    def test_user_with_purchase_can_create_review(self) -> None:
        self.create_purchase(user=self.user)
        self.client.force_login(self.user)

        response = self.client.post(
            self.product.get_absolute_url(),
            {"rating": "5", "comment": "  Чудова гра.  "},
        )

        self.assertRedirects(
            response,
            f"{self.product.get_absolute_url()}#reviews",
        )
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Чудова гра.")

    def test_duplicate_review_is_blocked(self) -> None:
        self.create_purchase(user=self.user)
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            comment="Перший відгук.",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self.product.get_absolute_url(),
            {"rating": "5", "comment": "Другий відгук."},
            follow=True,
        )

        self.assertEqual(Review.objects.count(), 1)
        self.assertContains(response, "Ви вже опублікували відгук про цю гру.")

    def test_invalid_rating_is_rejected(self) -> None:
        self.create_purchase(user=self.user)
        self.client.force_login(self.user)

        response = self.client.post(
            self.product.get_absolute_url(),
            {"rating": "6", "comment": "Неприпустима оцінка."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.exists())
        self.assertIn("rating", response.context["review_form"].errors)

    def test_product_detail_displays_created_review(self) -> None:
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment="Відгук на сторінці товару.",
        )

        response = self.client.get(self.product.get_absolute_url())

        self.assertContains(response, review.comment)
        self.assertContains(response, self.user.username)

    def test_average_rating_and_review_count_update(self) -> None:
        second_user = get_user_model().objects.create_user(
            username="second-reviewer",
            password="StrongPassword123!",
        )
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment="П'ять зірок.",
        )
        Review.objects.create(
            user=second_user,
            product=self.product,
            rating=3,
            comment="Три зірки.",
        )

        response = self.client.get(self.product.get_absolute_url())

        self.assertEqual(response.context["reviews_count"], 2)
        self.assertEqual(response.context["average_rating"], 4.0)
        self.assertContains(response, "4,0")
        self.assertContains(response, "Відгуків: 2")

    def test_popular_sort_uses_review_count(self) -> None:
        second_user = get_user_model().objects.create_user(
            username="popular-reviewer",
            password="StrongPassword123!",
        )
        less_popular_product = Product.objects.create(
            name="Less Popular Game",
            slug="less-popular-game",
            description="Another game.",
            price=Decimal("80.00"),
            category=self.product.category,
            platform=Product.Platform.PC,
            stock=5,
        )
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment="Перший відгук.",
        )
        Review.objects.create(
            user=second_user,
            product=self.product,
            rating=4,
            comment="Другий відгук.",
        )
        Review.objects.create(
            user=self.user,
            product=less_popular_product,
            rating=5,
            comment="Єдиний відгук.",
        )

        response = self.client.get(
            reverse("products:product_list"),
            {"sort": "popular"},
        )

        products = list(response.context["products"])
        self.assertEqual(products[0], self.product)

    def test_review_ui_uses_ukrainian_by_default(self) -> None:
        response = self.client.get(self.product.get_absolute_url())

        self.assertContains(response, "Хочете поділитися враженнями?")
        self.assertContains(response, "Увійти")

    def test_review_ui_can_be_rendered_in_english(self) -> None:
        response = self.client.get(
            self.product.get_absolute_url(),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, "Want to share your experience?")
        self.assertContains(response, "Log in")

    def create_purchase(self, *, user: Any) -> Order:
        order = Order.objects.create(
            user=user,
            total_price=self.product.price,
            first_name="Verified",
            last_name="Player",
            email="verified@example.com",
            phone="+380000000000",
            city="Kyiv",
            shipping_address="Test street, 1",
            payment_method=Order.PaymentMethod.BANK_CARD_TEST,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )
        return order
