"""Views for registration and authenticated account pages."""

from typing import Any

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView, ListView, TemplateView

from orders.constants import DEMO_ACTIVATION_KEY
from orders.models import Order
from users.forms import (
    AccountAuthenticationForm,
    AccountPasswordChangeForm,
    ProfileUpdateForm,
    RegistrationForm,
)


class RegisterView(FormView):
    """Register and immediately authenticate a new customer."""

    template_name = "users/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("account:dashboard")

    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        if request.user.is_authenticated:
            return redirect("account:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: RegistrationForm) -> HttpResponse:
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _("Обліковий запис успішно створено."))
        return super().form_valid(form)


class AccountLoginView(LoginView):
    """Authenticate a customer using Django session authentication."""

    template_name = "users/login.html"
    authentication_form = AccountAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, _("Ви успішно увійшли."))
        return response


class AccountLogoutView(LoginRequiredMixin, TemplateView):
    """Show logout confirmation and end the session on POST."""

    template_name = "users/logout.html"

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        logout(request)
        messages.success(request, _("Ви успішно вийшли."))
        return redirect("/")


class AccountDashboardView(LoginRequiredMixin, TemplateView):
    """Display basic account information and account navigation."""

    template_name = "users/dashboard.html"


class AccountProfileView(LoginRequiredMixin, FormView):
    """Edit the current user's digital account identity."""

    template_name = "users/profile.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("account:profile")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form: ProfileUpdateForm) -> HttpResponse:
        form.save()
        messages.success(self.request, _("Профіль успішно оновлено."))
        return super().form_valid(form)


class OrderHistoryView(LoginRequiredMixin, ListView):
    """List orders linked to the current authenticated customer."""

    model = Order
    template_name = "users/order_history.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Order]:
        user_id = self.request.user.pk
        if user_id is None:
            return Order.objects.none()
        return (
            Order.objects.filter(user_id=user_id)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Expose the shared placeholder key to the history template."""
        context = super().get_context_data(**kwargs)
        context["demo_activation_key"] = DEMO_ACTIVATION_KEY
        return context


class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Change a password while preserving the authenticated session."""

    template_name = "users/password_change.html"
    form_class = AccountPasswordChangeForm
    success_url = reverse_lazy("account:dashboard")

    def form_valid(self, form: PasswordChangeForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, _("Пароль успішно змінено."))
        return response
