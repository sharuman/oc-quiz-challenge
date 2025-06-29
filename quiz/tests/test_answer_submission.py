from django.urls import reverse
from rest_framework import status
from quiz.tests.base import BaseQuizTestCase
from quiz.models import Question, Choice, QuizParticipant, ParticipantAnswer

class AnswerSubmissionTests(BaseQuizTestCase):
    
    # Test if unauthenticated submission is rejected
    def test_submit_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test if submission before activation is forbidden
    def test_submit_before_activation_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test if submission after activation succeeds
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

    # Test if duplicate submission to same question is rejected
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

    # Test if submission from user with no participation record is rejected
    def test_submit_not_assigned_to_quiz(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)

        # Remove participant from quiz
        QuizParticipant.objects.filter(quiz=self.quiz, participant=self.participant).delete()

        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('not allowed', str(response.data).lower())

    # Test if submission to nonexistent quiz is rejected
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

    # Test if submission to nonexistent question is rejected
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

    # Test if submission of choice from another question is rejected
    def test_choice_of_another_question(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)

        other_question = Question.objects.create(
            quiz=self.quiz,
            text='Second question'
        )
        other_choice = Choice.objects.create(
            question=other_question,
            text='Invalid choice',
            is_correct=False
        )

        response = self.client.post(
            self.answer_url,
            {'selected_choice': other_choice.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not valid for this question', str(response.data).lower())

    # Test if submission of nonexistent choice ID is rejected
    def test_submit_with_nonexistent_choice_id(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)

        invalid_choice_id = 99999
        response = self.client.post(
            self.answer_url,
            {'selected_choice': invalid_choice_id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('does not exist', str(response.data).lower())

    # Test if submission without selected_choice is rejected
    def test_submit_without_choice(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.answer_url,
            {},  # no selected_choice
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('selected_choice', response.data)

    # Test if final submission marks quiz complete and sets score
    def test_submit_final_answer_marks_quiz_complete_and_sets_score(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)

        other_question = Question.objects.create(
            quiz=self.quiz,
            text='Second question'
        )
        Choice.objects.create(
            question=other_question,
            text='Yes',
            is_correct=True
        )
        Choice.objects.create(
            question=other_question,
            text='No',
            is_correct=False
        )
        # Submit answers for all but one question to set up near-complete state
        for q in self.quiz.questions.exclude(id=self.question.id):
            ParticipantAnswer.objects.create(
                participant=self.participant,
                quiz=self.quiz,
                question=q,
                selected_choice=q.choices.get(is_correct=True)
            )

        # Submit final answer
        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        qp = QuizParticipant.objects.get(pk=self.qp.pk)
        self.assertIsNotNone(qp.completed_at)
        self.assertIsNotNone(qp.score)

    # Test if partial completion does not mark quiz complete
    def test_partial_completion_does_not_mark_quiz_complete(self):
        self.activate(password='newpass')
        self.client.force_authenticate(user=self.user)

        other_question = Question.objects.create(
            quiz=self.quiz,
            text='Second question'
        )
        _ = Choice.objects.create(
            question=other_question,
            text='Valid choice',
            is_correct=True
        )

        # Submit only one answer in a multi-question quiz
        response = self.client.post(
            self.answer_url,
            {'selected_choice': self.choice_yes.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        qp = QuizParticipant.objects.get(pk=self.qp.pk)
        self.assertIsNone(qp.completed_at)
        self.assertIsNone(qp.score)
