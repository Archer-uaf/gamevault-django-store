"""Read-only REST API views for products and categories."""

from django.db.models import Avg, Count, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, viewsets

from products.filters import ProductFilter
from products.models import Category, Product
from products.ordering import EffectivePriceOrderingFilter
from products.querysets import with_effective_price
from products.serializers import CategorySerializer, ProductSerializer


@extend_schema_view(
    list=extend_schema(auth=[]),
    retrieve=extend_schema(auth=[]),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve active catalog products."""

    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        EffectivePriceOrderingFilter,
    )
    filterset_class = ProductFilter
    search_fields = ("name", "description", "description_en")
    ordering_fields = ("price", "created_at", "popularity")
    ordering = ("-created_at",)

    def get_queryset(self) -> QuerySet[Product]:
        return with_effective_price(
            Product.objects.filter(is_active=True)
            .select_related("category", "category__parent")
            .annotate(
                popularity=Count("reviews", distinct=True),
                average_rating=Avg("reviews__rating"),
            )
        )


@extend_schema_view(
    list=extend_schema(auth=[]),
    retrieve=extend_schema(auth=[]),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve catalog categories."""

    queryset = Category.objects.select_related("parent").all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
