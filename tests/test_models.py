from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils.translation import override

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


def test_product_money_and_percent_db_constraints(category: Category) -> None:
    invalid_products = (
        ("zero-price-game", Decimal("0.00"), 0, 1),
        ("large-discount-game", Decimal("10.00"), 91, 1),
        ("negative-stock-game", Decimal("10.00"), 0, -1),
    )

    for slug, price, discount_percent, stock in invalid_products:
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    name=slug,
                    slug=slug,
                    description="Invalid product.",
                    category=category,
                    platform=Product.Platform.PC,
                    price=price,
                    discount_percent=discount_percent,
                    stock=stock,
                )


def test_product_localized_description_uses_english_when_available(
    product: Product,
) -> None:
    product.description = "Український опис."
    product.description_en = "English description."

    with override("en"):
        assert product.localized_description == "English description."


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
        payment_method=Order.PaymentMethod.BANK_CARD_TEST,
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
        payment_method=Order.PaymentMethod.BANK_CARD_TEST,
    )
    item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=3,
        price=Decimal("19.99"),
    )

    assert item.total_price == Decimal("59.97")


def test_order_total_price_db_constraint(user: Any) -> None:
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Order.objects.create(
                user=user,
                total_price=Decimal("-0.01"),
                first_name="Alex",
                last_name="Player",
                email="alex@example.com",
                phone="+380000000000",
                city="Kyiv",
                shipping_address="Test street, 1",
                payment_method=Order.PaymentMethod.BANK_CARD_TEST,
            )


def test_order_item_price_and_quantity_db_constraints(
    user: Any,
    product: Product,
) -> None:
    order = Order.objects.create(
        user=user,
        first_name="Alex",
        last_name="Player",
        email="alex@example.com",
        phone="+380000000000",
        city="Kyiv",
        shipping_address="Test street, 1",
        payment_method=Order.PaymentMethod.BANK_CARD_TEST,
    )

    invalid_items = (
        {"quantity": 1, "price": Decimal("-0.01")},
        {"quantity": 0, "price": Decimal("10.00")},
    )
    for data in invalid_items:
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    **data,
                )


def test_create_review(user: Any, product: Product) -> None:
    review = Review.objects.create(
        user=user,
        product=product,
        rating=5,
        comment="Excellent game.",
    )

    assert review.pk is not None
    assert review.rating == 5


def test_review_rating_db_constraints(user: Any, product: Product) -> None:
    for rating in (0, 6):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    user=user,
                    product=product,
                    rating=rating,
                    comment="Invalid rating.",
                )


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
