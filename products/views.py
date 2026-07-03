"""Public pages related to the product catalog."""

from decimal import Decimal, InvalidOperation
from typing import Any

from django.db.models import Avg, Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from products.models import Category, Product


def home(request: HttpRequest) -> HttpResponse:
    """Render the static GameVault landing page."""
    return render(request, "pages/home.html")


def _parse_price(value: str) -> Decimal | None:
    """Convert a query parameter to a finite non-negative decimal."""
    if not value:
        return None
    try:
        price = Decimal(value)
    except InvalidOperation:
        return None
    if not price.is_finite() or price < 0:
        return None
    return price


class ProductListView(ListView):
    """Display active products with search, filters, sorting and pagination."""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 9

    SORT_OPTIONS = (
        ("newest", _("Спочатку нові")),
        ("price_asc", _("Ціна: за зростанням")),
        ("price_desc", _("Ціна: за спаданням")),
        ("popular", _("Популярні")),
    )
    SORT_FIELDS = {
        "newest": ("-created_at",),
        "price_asc": ("price",),
        "price_desc": ("-price",),
        "popular": ("-reviews_count", "-created_at"),
    }

    def get_queryset(self) -> QuerySet[Product]:
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .annotate(
                reviews_count=Count("reviews", distinct=True),
                average_rating=Avg("reviews__rating"),
            )
        )

        query = self.request.GET.get("q", "").strip()
        category_slug = self.request.GET.get("category", "").strip()
        platform = self.request.GET.get("platform", "").strip()
        min_price = _parse_price(self.request.GET.get("min_price", "").strip())
        max_price = _parse_price(self.request.GET.get("max_price", "").strip())

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(developer__icontains=query)
                | Q(publisher__icontains=query)
            )
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if platform:
            queryset = queryset.filter(platform=platform)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        sort = self.request.GET.get("sort", "newest")
        ordering = self.SORT_FIELDS.get(sort, self.SORT_FIELDS["newest"])
        return queryset.order_by(*ordering)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        selected_sort = self.request.GET.get("sort", "newest")
        if selected_sort not in self.SORT_FIELDS:
            selected_sort = "newest"

        context.update(
            {
                "categories": Category.objects.all(),
                "platform_choices": Product.Platform.choices,
                "current_filters": {
                    "q": self.request.GET.get("q", ""),
                    "category": self.request.GET.get("category", ""),
                    "platform": self.request.GET.get("platform", ""),
                    "min_price": self.request.GET.get("min_price", ""),
                    "max_price": self.request.GET.get("max_price", ""),
                    "sort": selected_sort,
                },
                "sort_options": self.SORT_OPTIONS,
            }
        )

        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["query_string"] = query_params.urlencode()
        return context


class ProductDetailView(DetailView):
    """Display one active product, its reviews and related games."""

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[Product]:
        return (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("reviews__user")
            .annotate(
                reviews_count=Count("reviews", distinct=True),
                average_rating=Avg("reviews__rating"),
            )
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        product = self.object
        context.update(
            {
                "reviews": product.reviews.all(),
                "average_rating": product.average_rating,
                "reviews_count": product.reviews_count,
                "related_products": (
                    Product.objects.filter(
                        is_active=True,
                        category=product.category,
                    )
                    .exclude(pk=product.pk)
                    .select_related("category")
                    .annotate(
                        reviews_count=Count("reviews", distinct=True),
                        average_rating=Avg("reviews__rating"),
                    )
                    .order_by("-is_featured", "-created_at")[:4]
                ),
            }
        )
        return context
