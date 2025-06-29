from django.urls import reverse
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from quiz.models import Quiz, Question, Choice, Participant, QuizParticipant

class BaseQuizTestCase(APITestCase):
    """
    Common setup for all quiz/participant tests.
    """
    def setUp(self):
        # create a participant user (inactive by default)
        self.user = CustomUser.objects.create_user(
            username='participant1',
            email='participant@example.com',
            password='initialpass',
            is_active=False,
            user_type=CustomUser.PARTICIPANT,
        )
        self.participant = Participant.objects.create(user=self.user)

        # create a quiz with one question + two choices
        self.quiz = Quiz.objects.create(
            title='Reality check quiz',
            description='',
            creator=self.user
        )
        self.question = Question.objects.create(quiz=self.quiz, text='Are we in the Matrix?')
        self.choice_yes = Choice.objects.create(
            question=self.question, text='Yes', is_correct=True
        )
        self.choice_no = Choice.objects.create(
            question=self.question, text='No', is_correct=False
        )

        # hook up the participant to the quiz (invitation token generated)
        self.qp = QuizParticipant.objects.create(
            quiz=self.quiz, participant=self.participant
        )

        # common URLs
        self.activation_url = reverse('participant-activate')
        self.answer_url = reverse(
            'submit-answer',
            args=[self.quiz.id, self.question.id]
        )

    def activate(self, token=None, password='newpass'):
        # if you don’t pass a token explicitly, it uses self.qp
        token = str(token or self.qp.invitation_token)
        return self.client.patch(
            reverse('participant-activate'),
            {'token': token, 'password': password},
            format='json'
        )
