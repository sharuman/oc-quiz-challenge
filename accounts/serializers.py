from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import now
from quiz.models import QuizParticipant
from rest_framework import serializers


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

        # Optional: clear the invitation token so it can’t be reused
        self.quiz_participant.invitation_token = None
        self.quiz_participant.accepted_at = now()
        self.quiz_participant.save()

        return user
