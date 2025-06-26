from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, SubmitAnswerView


router = DefaultRouter()

router.register(r'quizzes', QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
    path(
        "quizzes/<int:quiz_id>/questions/<int:question_id>/answers/",
        SubmitAnswerView.as_view(),
        name="submit-answer",
    ),
]
