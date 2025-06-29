from django.utils import timezone
from rest_framework import serializers
from .models import (
    Quiz,
    Question,
    Choice,
    ParticipantAnswer,
    Participant,
    QuizParticipant
)


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    selected_choice_id = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices', 'selected_choice_id']

    def get_selected_choice_id(self, question):
        user = self.context['request'].user
        try:
            participant = user.participant_profile
            answer = question.participantanswer_set.get(participant=participant)
            return answer.selected_choice_id
        except ParticipantAnswer.DoesNotExist:
            return None


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions']


class SubmitAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantAnswer
        fields = ['selected_choice']

    def validate(self, data):
        user = self.context['request'].user
        question = self.context.get('question')
        quiz = question.quiz
        
        try:
            participant = user.participant_profile
        except Participant.DoesNotExist:
            raise serializers.ValidationError("Participant profile not found.")

        # Check that user is assigned to this quiz
        is_participant = QuizParticipant.objects.filter(
            quiz=quiz, participant=participant
        ).exists()

        if not is_participant:
            raise serializers.ValidationError("You are not allowed to answer this quiz.")
        
        if ParticipantAnswer.objects.filter(
            participant=participant,
            quiz=quiz,
            question=question
        ).exists():
            raise serializers.ValidationError("You have already answered this question.")

        # Store for use in create()
        self.context.update({
            'quiz': quiz,
            'question': question,
            'participant': participant,
        })

        return data

    def create(self, validated_data):
        participant = self.context['participant']
        quiz = self.context['quiz']
        question = self.context['question']

        # 1) Mark quiz start if this is their first answer
        qp, _ = QuizParticipant.objects.get_or_create(
            quiz=quiz,
            participant=participant,
        )
        if qp.started_at is None:
            qp.started_at = timezone.now()
            qp.save(update_fields=['started_at'])

        # 2) Create or update the participant’s answer
        answer = ParticipantAnswer.objects.create(
            participant=participant,
            quiz=quiz,
            question=question,
            selected_choice=validated_data['selected_choice'],
        )

        # 3) Check if participant has answered all questions
        total_questions = quiz.questions.count()
        answered_count = ParticipantAnswer.objects.filter(
            participant=participant,
            quiz=quiz,
        ).count()

        if answered_count >= total_questions:
            # 4) Compute and store final score
            correct_count = ParticipantAnswer.objects.filter(
                participant=participant,
                quiz=quiz,
                selected_choice__is_correct=True
            ).count()
            qp.completed_at = timezone.now()
            qp.score = (correct_count / total_questions) * 100

        qp.save(update_fields=['started_at', 'completed_at', 'score'])
        
        return answer


class QuizProgressSerializer(serializers.Serializer):
    """
    Serializer for the quiz progress endpoint.
    """
    started_at = serializers.DateTimeField(allow_null=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    total_questions = serializers.IntegerField()
    answered = serializers.IntegerField()
    percent_complete = serializers.FloatField()
    current_score = serializers.FloatField()
    final_score = serializers.FloatField()
