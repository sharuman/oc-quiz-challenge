from rest_framework import viewsets
from .models import Quiz
from .serializers import QuizSerializer


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_queryset(self):
        user = self.request.user
        return Quiz.objects.filter(participants__user=user)

    # def get_queryset(self):
    #     return Quiz.objects.filter(
    #         quizparticipant__participant__user=self.request.user
    #     ).distinct()
