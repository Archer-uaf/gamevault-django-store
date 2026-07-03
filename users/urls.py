"""URL routes for the web account authentication flow."""

from django.urls import path

from users.views import (
    AccountDashboardView,
    AccountLoginView,
    AccountLogoutView,
    AccountPasswordChangeView,
    OrderHistoryView,
    RegisterView,
)

app_name = "account"

urlpatterns = [
    path("", AccountDashboardView.as_view(), name="dashboard"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("orders/", OrderHistoryView.as_view(), name="orders"),
    path("password/", AccountPasswordChangeView.as_view(), name="password"),
]
