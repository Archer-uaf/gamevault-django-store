"""Public pages related to the product catalog."""

from decimal import Decimal, InvalidOperation
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from products.models import Category, Product
from reviews.forms import ReviewForm
from reviews.models import Review
from reviews.services import user_has_purchased_product

HOME_GENRE_SLUGS = (
    "action",
    "rpg",
    "adventure",
    "horror",
    "strategy",
    "racing",
    "indie",
    "simulation",
    "open-world",
    "shooter",
)
HOME_RECOMMENDED_SLUGS = (
    "cyberpunk-2077",
    "the-witcher-3-wild-hunt",
    "elden-ring",
)
HOME_GENRE_LABELS = {
    "action": "Action",
    "rpg": "RPG",
    "adventure": "Adventure",
    "horror": "Horror",
    "strategy": "Strategy",
    "racing": "Racing",
    "indie": "Indie",
    "simulation": "Simulation",
    "open-world": "Open World",
    "shooter": "Shooter",
}


def home(request: HttpRequest) -> HttpResponse:
    """Render the storefront landing page with demo catalog data when seeded."""
    categories_by_slug = {
        category.slug: category
        for category in Category.objects.filter(slug__in=HOME_GENRE_SLUGS)
    }
    genre_cards = [
        {
            "category": categories_by_slug.get(slug),
            "slug": slug,
            "label": (
                categories_by_slug[slug].name
                if slug in categories_by_slug
                else HOME_GENRE_LABELS[slug]
            ),
            "icon": f"images/categories/{slug}.svg",
        }
        for slug in HOME_GENRE_SLUGS
    ]

    products_by_slug = {
        product.slug: product
        for product in Product.objects.filter(
            slug__in=HOME_RECOMMENDED_SLUGS,
            is_active=True,
        )
        .select_related("category")
    }
    recommended_products = [
        products_by_slug[slug]
        for slug in HOME_RECOMMENDED_SLUGS
        if slug in products_by_slug
    ]

    return render(
        request,
        "pages/home.html",
        {
            "genre_cards": genre_cards,
            "recommended_products": recommended_products,
        },
    )


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
        reviews = list(product.reviews.all())
        user_review = None
        has_purchased = False
        if self.request.user.is_authenticated:
            user_id = self.request.user.pk
            if user_id is not None:
                user_review = next(
                    (
                        review
                        for review in reviews
                        if review.user_id == user_id
                    ),
                    None,
                )
                has_purchased = user_has_purchased_product(
                    user_id=user_id,
                    product_id=product.pk,
                )
        can_review = has_purchased and user_review is None
        context.update(
            {
                "reviews": reviews,
                "average_rating": product.average_rating,
                "reviews_count": product.reviews_count,
                "user_review": user_review,
                "has_purchased": has_purchased,
                "can_review": can_review,
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
        if can_review:
            context.setdefault("review_form", ReviewForm())
        return context

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        """Create a review after rechecking authentication and purchase."""
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

        self.object = self.get_object()
        user_id = request.user.pk
        if user_id is None:
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

        if Review.objects.filter(product=self.object, user_id=user_id).exists():
            messages.info(
                request,
                _("Ви вже опублікували відгук про цю гру."),
            )
            return redirect(f"{self.object.get_absolute_url()}#reviews")

        if not user_has_purchased_product(
            user_id=user_id,
            product_id=self.object.pk,
        ):
            messages.error(
                request,
                _("Залишити відгук можна лише після покупки цієї гри."),
            )
            return redirect(f"{self.object.get_absolute_url()}#reviews")

        form = ReviewForm(request.POST)
        if not form.is_valid():
            context = self.get_context_data(review_form=form)
            return self.render_to_response(context)

        review = form.save(commit=False)
        review.product = self.object
        review.user = request.user
        try:
            with transaction.atomic():
                review.save()
        except IntegrityError:
            messages.info(
                request,
                _("Ви вже опублікували відгук про цю гру."),
            )
        else:
            messages.success(request, _("Дякуємо! Ваш відгук опубліковано."))

        return redirect(f"{self.object.get_absolute_url()}#reviews")
