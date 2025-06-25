from rest_framework import viewsets
from .models import Quiz
from .serializers import QuizSerializer


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
