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
from products.querysets import EFFECTIVE_PRICE_ANNOTATION, with_effective_price
from reviews.forms import ReviewForm
from reviews.models import Review
from reviews.services import user_has_purchased_product


HOME_GENRE_CARDS = (
    {
        "slug": "action",
        "label": _("Екшн"),
        "icon": "images/categories/action.svg",
        "class": "action",
    },
    {
        "slug": "rpg",
        "label": "RPG",
        "icon": "images/categories/rpg.svg",
        "class": "rpg",
    },
    {
        "slug": "adventure",
        "label": _("Пригоди"),
        "icon": "images/categories/adventure.svg",
        "class": "adventure",
    },
    {
        "slug": "horror",
        "label": _("Горор"),
        "icon": "images/categories/horror.svg",
        "class": "horror",
    },
    {
        "slug": "strategy",
        "label": _("Стратегії"),
        "icon": "images/categories/strategy.svg",
        "class": "strategy",
    },
    {
        "slug": "racing",
        "label": _("Гонки"),
        "icon": "images/categories/racing.svg",
        "class": "racing",
    },
    {
        "slug": "indie",
        "label": _("Інді"),
        "icon": "images/categories/indie.svg",
        "class": "indie",
    },
    {
        "slug": "simulation",
        "label": _("Симулятори"),
        "icon": "images/categories/simulation.svg",
        "class": "simulation",
    },
    {
        "slug": "open-world",
        "label": _("Відкритий світ"),
        "icon": "images/categories/open-world.svg",
        "class": "open-world",
    },
    {
        "slug": "shooter",
        "label": _("Шутери"),
        "icon": "images/categories/shooter.svg",
        "class": "shooter",
    },
)

HOME_HERO_SLUGS = (
    "cyberpunk-2077",
    "the-witcher-3-wild-hunt",
    "hearts-of-iron-iv",
)
HOME_RECOMMENDED_SLUGS = (
    "cyberpunk-2077",
    "the-witcher-3-wild-hunt",
    "hearts-of-iron-iv",
)
HOME_PLATFORM_CARDS = (
    {
        "value": Product.Platform.PC,
        "label": "PC",
        "icon": "images/platforms/pc.svg",
        "class": "pc",
    },
    {
        "value": Product.Platform.PLAYSTATION,
        "label": "PlayStation",
        "icon": "images/platforms/playstation.svg",
        "class": "playstation",
    },
    {
        "value": Product.Platform.XBOX,
        "label": "Xbox",
        "icon": "images/platforms/xbox.svg",
        "class": "xbox",
    },
    {
        "value": Product.Platform.NINTENDO_SWITCH,
        "label": "Nintendo Switch",
        "icon": "images/platforms/nintendo-switch.svg",
        "class": "switch",
    },
)


def _products_by_slugs(slugs: tuple[str, ...]) -> list[Product]:
    """Return active products ordered by the supplied slug sequence."""
    products = (
        Product.objects.filter(
            is_active=True,
            slug__in=slugs,
        )
        .select_related("category")
        .prefetch_related("genres")
    )

    products_by_slug = {product.slug: product for product in products}
    return [
        product
        for slug in slugs
        if (product := products_by_slug.get(slug)) is not None
    ]


def home(request: HttpRequest) -> HttpResponse:
    """Render the GameVault landing page using real catalog records."""
    context = {
        "genre_cards": HOME_GENRE_CARDS,
        "platform_cards": HOME_PLATFORM_CARDS,
        "hero_products": _products_by_slugs(HOME_HERO_SLUGS),
        "recommended_products": _products_by_slugs(HOME_RECOMMENDED_SLUGS),
    }
    return render(request, "pages/home.html", context)


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


def build_page_window(
    *,
    current_page: int,
    total_pages: int,
    siblings: int = 2,
) -> list[int | str]:
    """Return compact page numbers with ellipsis gaps for pagination."""
    if total_pages <= 1:
        return [1]

    visible_pages = {1, total_pages}
    start = max(1, current_page - siblings)
    end = min(total_pages, current_page + siblings)
    visible_pages.update(range(start, end + 1))

    page_window: list[int | str] = []
    previous_page = 0
    for page_number in sorted(visible_pages):
        if previous_page and page_number - previous_page > 1:
            page_window.append("ellipsis")
        page_window.append(page_number)
        previous_page = page_number
    return page_window


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
        "price_asc": (EFFECTIVE_PRICE_ANNOTATION,),
        "price_desc": (f"-{EFFECTIVE_PRICE_ANNOTATION}",),
        "popular": ("-reviews_count", "-created_at"),
    }

    def get_queryset(self) -> QuerySet[Product]:
        queryset = with_effective_price(
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("genres")
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
                | Q(description_en__icontains=query)
                | Q(developer__icontains=query)
                | Q(publisher__icontains=query)
            )
        if category_slug:
            queryset = queryset.filter(
                Q(category__slug=category_slug)
                | Q(genres__slug=category_slug)
            ).distinct()
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
        context["page_window"] = build_page_window(
            current_page=context["page_obj"].number,
            total_pages=context["page_obj"].paginator.num_pages,
        )
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
            .prefetch_related("genres", "reviews__user")
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
                    Product.objects.filter(is_active=True)
                    .filter(
                        Q(category=product.category)
                        | Q(genres__in=product.genres.all())
                    )
                    .exclude(pk=product.pk)
                    .select_related("category")
                    .distinct()
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
