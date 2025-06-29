from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from quiz.models import Participant, Quiz, Question, Choice


class Command(BaseCommand):
    help = 'Seeds the database with a participant, quizzes, questions, and choices.'

    def handle(self, *args, **kwargs):
        # Create participant user
        participant_user, _ = CustomUser.objects.get_or_create(
            email='participant@example.com',
            defaults={
                'username': 'participant',
                'user_type': CustomUser.PARTICIPANT,
                'is_active': False,
            }
        )

        # Create participant profile
        participant, _ = Participant.objects.get_or_create(user=participant_user)

        # Fetch any existing creator user (assumes it's already created)
        creator = CustomUser.objects.filter(user_type=CustomUser.CREATOR).first()
        if not creator:
            self.stdout.write(self.style.ERROR('No creator user found. Please create a user with user_type="creator".'))
            return

        # Create quiz
        quiz, _ = Quiz.objects.get_or_create(
            title='General Knowledge Quiz',
            defaults={
                'description': 'A test of general knowledge.',
                'creator': creator,
                'created_at': timezone.now()
            }
        )

        # Create questions and choices
        q1, _ = Question.objects.get_or_create(
            quiz=quiz,
            text='What is the capital of France?'
        )
        Choice.objects.get_or_create(question=q1, text='Paris', is_correct=True)
        Choice.objects.get_or_create(question=q1, text='London', is_correct=False)
        Choice.objects.get_or_create(question=q1, text='Berlin', is_correct=False)

        q2, _ = Question.objects.get_or_create(
            quiz=quiz,
            text='Which planet is known as the Red Planet?'
        )
        Choice.objects.get_or_create(question=q2, text='Mars', is_correct=True)
        Choice.objects.get_or_create(question=q2, text='Earth', is_correct=False)
        Choice.objects.get_or_create(question=q2, text='Jupiter', is_correct=False)

        self.stdout.write(self.style.SUCCESS('Database seeded with participant and quiz content.'))
