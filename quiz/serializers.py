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

        quiz_id = self.context.get('quiz_id')
        question_id = self.context.get('question_id')

        if not quiz_id or not question_id:
            raise serializers.ValidationError("Quiz and question must be provided.")
        
        try:
            participant = user.participant_profile
        except Participant.DoesNotExist:
            raise serializers.ValidationError("Participant profile not found.")

        try:
            quiz = Quiz.objects.get(id=quiz_id)
            question = Question.objects.get(id=question_id, quiz=quiz)
        except (Quiz.DoesNotExist, Question.DoesNotExist):
            raise serializers.ValidationError("Invalid quiz or question.")

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
        return ParticipantAnswer.objects.update_or_create(
            participant=self.context['participant'],
            quiz=self.context['quiz'],
            question=self.context['question'],
            defaults={'selected_choice': validated_data['selected_choice']},
        )[0]
