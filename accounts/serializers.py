from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model, authenticate
from django.utils.timezone import now
from quiz.models import QuizParticipant
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from accounts.models import UserToken


class ParticipantActivationSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from quiz.models import QuizParticipant

        try:
            quiz_participant = QuizParticipant.objects.select_related("participant__user").get(
                invitation_token=data["token"]
            )
        except QuizParticipant.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired invitation token.")

        user = quiz_participant.participant.user
        if user.is_active:
            raise serializers.ValidationError("User already activated.")

        self.user = user
        self.quiz_participant = quiz_participant
        return data

    def save(self):
        user = self.user
        user.set_password(self.validated_data["password"])
        user.is_active = True
        user.save()

        self.quiz_participant.invitation_token = None
        self.quiz_participant.accepted_at = now()
        self.quiz_participant.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        UserToken.objects.update_or_create(
            user=user,
            defaults={"access_token": access, "refresh_token": str(refresh)}
        )

        return {
            "access": access,
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "user_type": user.user_type,
            }
        }


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        refresh_token = data.get("refresh")
        if not refresh_token:
            raise serializers.ValidationError("Refresh token is required.")

        try:
            old_refresh = RefreshToken(refresh_token)
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")

        user_id = old_refresh.get("user_id")
        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("User not found.")

        new_refresh = RefreshToken.for_user(user)
        new_access = str(new_refresh.access_token)

        UserToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": new_access,
                "refresh_token": str(new_refresh),
            }
        )

        return {
            "access": new_access,
            "refresh": str(new_refresh)
        }
