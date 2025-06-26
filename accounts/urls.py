from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import ActivateParticipantView, LoginView, RefreshTokenView, ProtectedMeView


urlpatterns = [
    path("activate/", ActivateParticipantView.as_view(), name="participant-activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("me/", ProtectedMeView.as_view(), name="me"),
]
