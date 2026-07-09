"""URL routes for the GameVault REST API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from orders.api_views import (
    CartAPIView,
    CartItemCreateAPIView,
    CartItemDetailAPIView,
    OrderViewSet,
)
from products.api_views import CategoryViewSet, ProductViewSet
from reviews.api_views import ReviewViewSet
from users.api_views import (
    CurrentUserAPIView,
    EmailOrUsernameTokenObtainPairView,
    RegisterAPIView,
)

app_name = "api"

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("orders", OrderViewSet, basename="order")
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
    path("cart/", CartAPIView.as_view(), name="cart"),
    path("cart/items/", CartItemCreateAPIView.as_view(), name="cart-item-add"),
    path(
        "cart/items/<int:product_id>/",
        CartItemDetailAPIView.as_view(),
        name="cart-item-detail",
    ),
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/token/", EmailOrUsernameTokenObtainPairView.as_view(), name="token"),
    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path("auth/me/", CurrentUserAPIView.as_view(), name="me"),
]
