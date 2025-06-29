from rest_framework import permissions
from quiz.models import QuizParticipant

class IsActivatedParticipant(permissions.BasePermission):
    message = "You must accept the invitation before submitting answers."

    def has_permission(self, request, view):
        quiz_id = view.kwargs.get('quiz_id')
        try:
            qp = QuizParticipant.objects.get(
                quiz_id=quiz_id,
                participant=request.user.participant_profile
            )
        except QuizParticipant.DoesNotExist:
            return False
        return qp.accepted_at is not None
