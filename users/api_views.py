"""REST API views for registration and current-user data."""

from typing import Any

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions

from users.serializers import RegisterSerializer, UserSerializer


@extend_schema_view(post=extend_schema(auth=[]))
class RegisterAPIView(generics.CreateAPIView):
    """Register a new user account."""

    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CurrentUserAPIView(generics.RetrieveAPIView):
    """Return identity data for the authenticated user."""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> Any:
        return self.request.user
