from django.urls import reverse
from rest_framework import status
from quiz.tests.base import BaseQuizTestCase
from quiz.models import QuizParticipant

class InvitationFlowTests(BaseQuizTestCase):

    # Test if unauthenticated submission is rejected
    def test_submit_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test if submission before activation is forbidden
    def test_submit_before_activation_forbidden(self):
        # User is inactive and hasn't activated via token
        answer_url = reverse('submit-answer', args=[self.quiz.id, self.question.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test if activation succeeds and sets user active, clears token, returns JWTs
    def test_activation_success(self):
        response = self.activate(password='newpassword')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        qp = QuizParticipant.objects.get(pk=self.qp.pk)
        self.assertTrue(self.user.is_active)
        self.assertIsNone(qp.invitation_token)
        self.assertIsNotNone(qp.accepted_at)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.user.email)

    # Test if activation cannot be used twice
    def test_activation_invalid_token(self):
        response = self.activate(token='invalid-token', password='invalid-pass')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data.get('non_field_errors') or []
        self.assertTrue(
            any('valid uuid' in str(err).lower() for err in errors)
        )

    # Test if activation cannot be used twice
    def test_activation_twice(self):
        # First activation
        response1 = self.activate(password='firstpass')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        # Second activation should fail with same token
        response2 = self.activate(password='secondpass')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response2.data.get('non_field_errors') or []
        self.assertTrue(
            any('expired' in str(err).lower() or 'invalid' in str(err).lower() for err in errors)
        )
