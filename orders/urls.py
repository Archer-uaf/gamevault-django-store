"""URL routes for the session shopping cart."""

from django.urls import path

from orders.views import CartAddView, CartDetailView, CartRemoveView, CartUpdateView

app_name = "cart"

urlpatterns = [
    path("", CartDetailView.as_view(), name="detail"),
    path("add/<int:product_id>/", CartAddView.as_view(), name="add"),
    path("update/<int:product_id>/", CartUpdateView.as_view(), name="update"),
    path("remove/<int:product_id>/", CartRemoveView.as_view(), name="remove"),
]
