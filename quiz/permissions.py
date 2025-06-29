from rest_framework import permissions
from quiz.models import QuizParticipant


class IsActivatedParticipant(permissions.BasePermission):
    message = "You must accept the invitation before submitting answers."

    def has_object_permission(self, request, view, obj):
        participant = getattr(request.user, 'participant_profile', None)
        if not participant:
            return False

        try:
            qp = QuizParticipant.objects.get(
                quiz=obj.quiz,
                participant=request.user.participant_profile
            )
        except QuizParticipant.DoesNotExist:
            return False

        return qp.accepted_at is not None
