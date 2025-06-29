from django.urls import reverse
from rest_framework import status
from quiz.tests.base import BaseQuizTestCase
from quiz.models import QuizParticipant, ParticipantAnswer

class AnswerSubmissionTests(BaseQuizTestCase):

    def test_submit_before_activation_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_after_activation(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        qp = QuizParticipant.objects.get(pk=self.qp.pk)
        self.assertIsNotNone(qp.started_at)
        pa = ParticipantAnswer.objects.get(participant=self.participant, question=self.question)
        self.assertEqual(pa.selected_choice, self.choice_yes)

    def test_answer_twice_same_question(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)
        response1 = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already answered', str(response2.data).lower())

    def test_answer_nonexistent_quiz(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)
        wrong_url = reverse('submit-answer', args=[self.quiz.id + 999, self.question.id])
        response = self.client.post(
            wrong_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_answer_nonexistent_question(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)
        wrong_url = reverse('submit-answer', args=[self.quiz.id, self.question.id + 999])
        response = self.client.post(
            wrong_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
