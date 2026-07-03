from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from orders.models import Order, OrderItem
from products.models import Category, Product
from reviews.models import Review
from users.models import UserProfile

pytestmark = pytest.mark.django_db


@pytest.fixture
def category() -> Category:
    return Category.objects.create(name="Action", slug="action")


@pytest.fixture
def product(category: Category) -> Product:
    return Product.objects.create(
        name="Example Game",
        slug="example-game",
        description="A game used by model tests.",
        price=Decimal("100.00"),
        category=category,
        platform=Product.Platform.PC,
        stock=5,
    )


@pytest.fixture
def user() -> Any:
    user_model = get_user_model()
    return user_model.objects.create_user(
        username="player",
        email="player@example.com",
        password="test-password",
    )


def test_create_category() -> None:
    category = Category.objects.create(name="Role-playing", slug="role-playing")

    assert category.pk is not None
    assert str(category) == "Role-playing"


def test_create_product(product: Product, category: Category) -> None:
    assert product.pk is not None
    assert product.category == category
    assert product.platform == Product.Platform.PC
    assert str(product) == "Example Game"


def test_product_final_price(product: Product) -> None:
    product.discount_percent = 15

    assert product.final_price == Decimal("85.00")


def test_product_has_discount(product: Product) -> None:
    assert product.has_discount is False

    product.discount_percent = 10

    assert product.has_discount is True


def test_product_is_in_stock(product: Product) -> None:
    assert product.is_in_stock is True

    product.stock = 0

    assert product.is_in_stock is False


def test_user_profile_is_created_automatically(user: Any) -> None:
    profile = UserProfile.objects.get(user=user)

    assert profile.user == user


def test_create_order_and_order_item(user: Any, product: Product) -> None:
    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_price=Decimal("100.00"),
        first_name="Alex",
        last_name="Player",
        email="alex@example.com",
        phone="+380000000000",
        city="Kyiv",
        shipping_address="Test street, 1",
        payment_method=Order.PaymentMethod.CARD,
    )
    item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=Decimal("50.00"),
    )

    assert order.pk is not None
    assert item.pk is not None
    assert item.order == order


def test_order_item_total_price(user: Any, product: Product) -> None:
    order = Order.objects.create(
        user=user,
        first_name="Alex",
        last_name="Player",
        email="alex@example.com",
        phone="+380000000000",
        city="Kyiv",
        shipping_address="Test street, 1",
        payment_method=Order.PaymentMethod.CASH_ON_DELIVERY,
    )
    item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=3,
        price=Decimal("19.99"),
    )

    assert item.total_price == Decimal("59.97")


def test_create_review(user: Any, product: Product) -> None:
    review = Review.objects.create(
        user=user,
        product=product,
        rating=5,
        comment="Excellent game.",
    )

    assert review.pk is not None
    assert review.rating == 5


def test_user_cannot_review_same_product_twice(
    user: Any,
    product: Product,
) -> None:
    Review.objects.create(
        user=user,
        product=product,
        rating=5,
        comment="First review.",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Review.objects.create(
                user=user,
                product=product,
                rating=4,
                comment="Second review.",
            )
