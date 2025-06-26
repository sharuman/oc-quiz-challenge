from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import ParticipantActivationSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes


class ActivateParticipantView(APIView):

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
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "user_type": user.user_type,
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
