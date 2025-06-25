from django.db import models
from django.utils import timezone
from oper import settings
from accounts.models import CustomUser
import uuid


# NOTE: use this model for participant-related global metadata (e.g. display name, avatar, stats)
class Participant(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": CustomUser.PARTICIPANT},
        related_name='participant_profile'
    )

    def __str__(self):
        return f"Participant: {self.user.email}"


# Pivot model betwen Quiz and Participiant
class QuizParticipant(models.Model):
    invited_at = models.DateTimeField(default=timezone.now)
    invitation_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    accepted = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('participant', 'quiz')

    def save(self, *args, **kwargs):
        if not self.invitation_token:
            self.invitation_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.participant.user.email} in {self.quiz.title}"


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_quizzes"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    participants = models.ManyToManyField(
        'Participant',
        through='QuizParticipant',
        related_name='quizzes'
    )

    def __str__(self):
        return self.title


class Question(models.Model):
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.text


class Choice(models.Model):
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationships
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')

    def __str__(self):
        return self.text
