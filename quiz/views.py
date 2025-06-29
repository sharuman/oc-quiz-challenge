from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Quiz, QuizParticipant, ParticipantAnswer
from .serializers import QuizSerializer, QuizDetailSerializer, SubmitAnswerSerializer


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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer  # shows nested questions + answers
        return QuizSerializer
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        quiz = get_object_or_404(self.get_queryset(), pk=pk)

        try:
            qp = QuizParticipant.objects.get(
                quiz=quiz,
                participant=request.user.participant_profile
            )
        except QuizParticipant.DoesNotExist:
            return Response(
                {"detail": "You are not a participant of this quiz."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        total = quiz.questions.count()
        answered = ParticipantAnswer.objects.filter(
            quiz=quiz, participant=qp.participant
        ).count()
        correct = ParticipantAnswer.objects.filter(
            quiz=quiz,
            participant=qp.participant,
            selected_choice__is_correct=True
        ).count()

        return Response({
            "started_at":       qp.started_at,
            "completed_at":     qp.completed_at,
            "total_questions":  total,
            "answered":         answered,
            "percent_complete": round(answered / total * 100, 2) if total else 0,
            "current_score":    round(correct  / total * 100, 2) if total else 0,
            "final_score":      qp.score,
        })


@extend_schema(
    tags=["quizzes"],
    request=SubmitAnswerSerializer,
    responses={201: OpenApiResponse(description="Answer submitted successfully")}
)
class SubmitAnswerView(APIView):
    def post(self, request, quiz_id, question_id):
        serializer = SubmitAnswerSerializer(
            data=request.data,
            context={
                'request': request,
                'quiz_id': quiz_id,
                'question_id': question_id,
            }
        )
        if serializer.is_valid():
            answer = serializer.save()
            return Response({
                "message": "Answer submitted successfully.",
                "answer_id": answer.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
