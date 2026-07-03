"""Public-read and authenticated-create REST API views for reviews."""

from typing import Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, viewsets

from reviews.models import Review
from reviews.serializers import ReviewSerializer


@extend_schema_view(list=extend_schema(auth=[]))
class ReviewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """List reviews publicly and create verified-purchase reviews."""

    serializer_class = ReviewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("product",)

    def get_queryset(self) -> QuerySet[Review]:
        return Review.objects.select_related("product", "user").all()

    def get_permissions(self) -> list[Any]:
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer: ReviewSerializer) -> None:
        serializer.save(user=self.request.user)
