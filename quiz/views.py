from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Quiz
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
