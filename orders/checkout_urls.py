"""URL routes for the guest web checkout flow."""

from django.urls import path

from orders.checkout_views import CheckoutSuccessView, CheckoutView

app_name = "checkout"

urlpatterns = [
    path("", CheckoutView.as_view(), name="form"),
    path("success/<int:order_id>/", CheckoutSuccessView.as_view(), name="success"),
]
