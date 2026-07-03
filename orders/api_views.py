"""REST API views for orders and the session-backed cart."""

from typing import Any, cast

from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, permissions, serializers, status, views, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from orders.cart import Cart
from orders.models import Order
from orders.serializers import (
    CartAddItemSerializer,
    CartOutputSerializer,
    CartUpdateItemSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from products.models import Product


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """List, retrieve, and create only the current user's orders."""

    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet[Order]:
        user_id = self.request.user.pk
        if user_id is None:
            return Order.objects.none()
        return (
            Order.objects.filter(user_id=user_id)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def get_serializer_class(self) -> type[Any]:
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output = OrderSerializer(order, context=self.get_serializer_context())
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)


class CartAPIView(views.APIView):
    """Return or clear the anonymous/authenticated session cart."""

    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        responses=CartOutputSerializer,
        description="Return the current session cart.",
    )
    def get(self, request: Request) -> Response:
        """Return the current session cart."""
        return Response(_serialize_cart(_get_cart(request)))

    @extend_schema(
        responses={204: OpenApiResponse(description="Cart cleared.")},
        description="Clear the current session cart.",
    )
    def delete(self, request: Request) -> Response:
        """Clear the current session cart."""
        _get_cart(request).clear()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemCreateAPIView(views.APIView):
    """Add a product to the current session cart."""

    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        request=CartAddItemSerializer,
        responses={201: CartOutputSerializer},
        description="Add a product to the current session cart.",
    )
    def post(self, request: Request) -> Response:
        """Add a product quantity to the current session cart."""
        serializer = CartAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(
            Product,
            pk=serializer.validated_data["product_id"],
            is_active=True,
        )
        cart = _get_cart(request)
        try:
            cart.add(product, serializer.validated_data["quantity"])
        except ValueError as error:
            raise serializers.ValidationError(
                {"quantity": _("Недостатньо товару на складі.")}
            ) from error

        return Response(_serialize_cart(cart), status=status.HTTP_201_CREATED)


class CartItemDetailAPIView(views.APIView):
    """Update or remove one product in the current session cart."""

    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        request=CartUpdateItemSerializer,
        responses=CartOutputSerializer,
        description="Update a product quantity in the current session cart.",
    )
    def patch(self, request: Request, product_id: int) -> Response:
        """Replace one product quantity in the current session cart."""
        serializer = CartUpdateItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        cart = _get_cart(request)
        try:
            cart.update(product, serializer.validated_data["quantity"])
        except ValueError as error:
            raise serializers.ValidationError(
                {"quantity": _("Недостатньо товару на складі.")}
            ) from error

        return Response(_serialize_cart(cart))

    @extend_schema(
        responses={204: OpenApiResponse(description="Cart item removed.")},
        description="Remove a product from the current session cart.",
    )
    def delete(self, request: Request, product_id: int) -> Response:
        """Remove one product from the current session cart."""
        product = get_object_or_404(Product, pk=product_id)
        _get_cart(request).remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)


def _get_cart(request: Request) -> Cart:
    """Build the session cart service from a DRF request."""
    return Cart(cast(HttpRequest, request._request))


def _serialize_cart(cart: Cart) -> Any:
    """Return API-safe cart data with current catalog prices."""
    items = cart.get_items()
    payload = {
        "items": [
            {
                "product": {
                    "id": item.product.pk,
                    "name": item.product.name,
                    "slug": item.product.slug,
                },
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_total": item.total_price,
                "is_available": item.is_available,
            }
            for item in items
        ],
        "total": cart.get_total_price(items),
        "total_items": len(cart),
    }
    return CartOutputSerializer(payload).data
