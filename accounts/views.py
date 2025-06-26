from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import (
    ParticipantActivationSerializer,
    LoginSerializer,
    TokenRefreshSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import UserToken


class ActivateParticipantView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ParticipantActivationSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="Activate user using token and password.",
        examples=[
            OpenApiExample(
                name="Example Activation",
                value={
                    "token": "593357d3-f22a-493a-b1e5-808bd9ac4fcb",
                    "password": "StrongPass!123"
                },
                request_only=True,
            )
        ]
    )
    def patch(self, request):
        serializer = ParticipantActivationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            UserToken.objects.update_or_create(
                user=user,
                defaults={"access_token": str(refresh.access_token), "refresh_token": str(refresh)}
            )

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "email": user.email,
                    "user_type": user.user_type,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="User login via username and password.",
        examples=[
            OpenApiExample(
                name="Example Activation",
                value={
                    "username": "participant",
                    "password": "StrongPass!123"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        error = serializer.errors.get("non_field_errors") or serializer.errors.get("username")
        return Response({"detail": error[0] if error else "Invalid input."}, status=status.HTTP_401_UNAUTHORIZED)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=TokenRefreshSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="Generate new refresh and access tokens.",
        examples=[
            OpenApiExample(
                name="Example Activation",
                value={
                    "access": "abc",
                    "refresh": "xyz"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if not request.data.get("refresh"):
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        # Customize error response
        error = serializer.errors.get("non_field_errors") or serializer.errors.get("refresh")
        return Response({"detail": error[0] if error else "Invalid input."}, status=status.HTTP_401_UNAUTHORIZED)
