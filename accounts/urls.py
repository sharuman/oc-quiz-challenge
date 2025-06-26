from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import ActivateParticipantView


urlpatterns = [
    path("users/activate/", ActivateParticipantView.as_view(), name="participant-activate"),
]
