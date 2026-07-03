from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from orders.cart import CART_SESSION_KEY
from products.models import Category, Product


class SessionCartTests(TestCase):
    category: Category
    product: Product
    second_product: Product
    out_of_stock_product: Product

    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = Category.objects.create(name="Action", slug="action")
        cls.product = cls.create_product(
            name="Neon Test",
            slug="neon-test",
            price=Decimal("100.00"),
            stock=3,
            discount_percent=10,
        )
        cls.second_product = cls.create_product(
            name="Second Test",
            slug="second-test",
            price=Decimal("50.00"),
            stock=5,
        )
        cls.out_of_stock_product = cls.create_product(
            name="Unavailable Test",
            slug="unavailable-test",
            price=Decimal("75.00"),
            stock=0,
        )

    @classmethod
    def create_product(
        cls,
        *,
        name: str,
        slug: str,
        price: Decimal,
        stock: int,
        discount_percent: int = 0,
    ) -> Product:
        return Product.objects.create(
            name=name,
            slug=slug,
            description=f"Description for {name}",
            price=price,
            category=cls.category,
            platform=Product.Platform.PC,
            stock=stock,
            discount_percent=discount_percent,
            is_active=True,
        )

    def test_empty_cart_page_returns_200(self) -> None:
        response = self.client.get(reverse("cart:detail"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/cart_detail.html")
        self.assertContains(response, "Ваш кошик порожній")

    def test_product_detail_contains_add_to_cart_form(self) -> None:
        response = self.client.get(self.product.get_absolute_url())

        self.assertContains(response, reverse("cart:add", args=[self.product.pk]))
        self.assertContains(response, 'name="quantity"')

    def test_add_product_stores_quantity_in_session(self) -> None:
        response = self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 2},
        )

        self.assertRedirects(response, self.product.get_absolute_url())
        self.assertEqual(
            self.client.session[CART_SESSION_KEY],
            {str(self.product.pk): {"quantity": 2}},
        )

    def test_adding_same_product_increases_quantity(self) -> None:
        add_url = reverse("cart:add", args=[self.product.pk])

        self.client.post(add_url, {"quantity": 1})
        self.client.post(add_url, {"quantity": 2})

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.product.pk)][
                "quantity"
            ],
            3,
        )

    def test_add_rejects_quantity_above_stock(self) -> None:
        add_url = reverse("cart:add", args=[self.product.pk])
        self.client.post(add_url, {"quantity": 2})

        response = self.client.post(
            add_url,
            {"quantity": 2},
            follow=True,
        )

        self.assertContains(response, "доступно одиниць: 3")
        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.product.pk)][
                "quantity"
            ],
            2,
        )

    def test_out_of_stock_product_cannot_be_added(self) -> None:
        response = self.client.post(
            reverse("cart:add", args=[self.out_of_stock_product.pk]),
            {"quantity": 1},
            follow=True,
        )

        self.assertContains(response, "доступно одиниць: 0")
        self.assertNotIn(
            str(self.out_of_stock_product.pk),
            self.client.session.get(CART_SESSION_KEY, {}),
        )

    def test_update_replaces_quantity(self) -> None:
        self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 1},
        )

        response = self.client.post(
            reverse("cart:update", args=[self.product.pk]),
            {"quantity": 3},
        )

        self.assertRedirects(response, reverse("cart:detail"))
        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.product.pk)][
                "quantity"
            ],
            3,
        )

    def test_update_rejects_quantity_above_stock(self) -> None:
        self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 1},
        )

        self.client.post(
            reverse("cart:update", args=[self.product.pk]),
            {"quantity": 4},
        )

        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.product.pk)][
                "quantity"
            ],
            1,
        )

    def test_remove_deletes_product_from_session(self) -> None:
        self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 1},
        )

        response = self.client.post(
            reverse("cart:remove", args=[self.product.pk]),
        )

        self.assertRedirects(response, reverse("cart:detail"))
        self.assertNotIn(
            str(self.product.pk),
            self.client.session.get(CART_SESSION_KEY, {}),
        )

    def test_cart_calculates_discounted_total(self) -> None:
        self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 2},
        )
        self.client.post(
            reverse("cart:add", args=[self.second_product.pk]),
            {"quantity": 1},
        )

        response = self.client.get(reverse("cart:detail"))

        self.assertEqual(response.context["cart_total"], Decimal("230.00"))
        self.assertEqual(len(response.context["cart_items"]), 2)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.second_product.name)

    def test_header_displays_total_unit_count(self) -> None:
        self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 2},
        )
        self.client.post(
            reverse("cart:add", args=[self.second_product.pk]),
            {"quantity": 1},
        )

        response = self.client.get(reverse("cart:detail"))

        self.assertContains(response, "Товарів у кошику: 3")

    def test_cart_page_and_message_can_be_rendered_in_english(self) -> None:
        response = self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 1},
            HTTP_ACCEPT_LANGUAGE="en",
            follow=True,
        )

        self.assertContains(response, "added to the cart")

        response = self.client.get(
            reverse("cart:detail"),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, "Shopping cart")
        self.assertContains(response, "Total amount")
        self.assertContains(response, "Continue shopping")
