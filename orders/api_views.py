"""Authenticated REST API views for user-owned orders."""

from typing import Any

from django.db.models import QuerySet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderCreateSerializer, OrderSerializer


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
