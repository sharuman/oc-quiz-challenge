from django.contrib import admin
from django.db.models import Avg
from .models import Choice, Participant, ParticipantAnswer, Question, Quiz, QuizParticipant


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    exclude = ("created_at",)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    exclude = ("created_at",)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    exclude = ("created_at",)
    list_display = ('user__username', 'email', 'full_name', 'created_at', 'updated_at')
    search_fields = ['user__email']

    def email(self, obj):
        return obj.user.email

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class QuizParticipantInline(admin.TabularInline):
    model = QuizParticipant
    fields = (
        'participant', 
        'started_at', 
        'completed_at', 
        'percent_complete', 
        'score'
    )
    readonly_fields = (
        'started_at', 
        'completed_at', 
        'percent_complete', 
        'score'
    )
    extra = 0

    def percent_complete(self, obj):
        total = obj.quiz.questions.count()
        if not total:
            return "0 %"
        answered = obj.participantanswer_set.count()
        return f"{answered / total * 100:.2f} %"

    percent_complete.short_description = 'Progress'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'creator', 
        'participant_count',
        'started_count', 
        'completed_count', 
        'average_score'
    )
    exclude = ("created_at",)
    readonly_fields = ("creator",)
    search_fields = ['title']
    inlines = [QuestionInline, QuizParticipantInline]

    def participant_count(self, obj):
        """Total number of invited participants."""
        return obj.quizparticipant_set.count()
    participant_count.short_description = 'Invited'

    def started_count(self, obj):
        """How many have started (started_at is not null)."""
        return obj.quizparticipant_set.filter(started_at__isnull=False).count()
    started_count.short_description = 'Started'

    def completed_count(self, obj):
        """How many have completed (completed_at is not null)."""
        return obj.quizparticipant_set.filter(completed_at__isnull=False).count()
    completed_count.short_description = 'Completed'

    def average_score(self, obj):
        """Average of all non-null scores."""
        avg = obj.quizparticipant_set.filter(score__isnull=False) \
                  .aggregate(avg_score=Avg('score'))['avg_score']
        return f"{avg:.2f}" if avg is not None else '-'
    average_score.short_description = 'Avg Score'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.save()


@admin.register(QuizParticipant)
class QuizParticipantAdmin(admin.ModelAdmin):
    list_display = ['participant', 'quiz', 'invited_at', 'accepted', 'score']
    exclude = ("created_at",)
    # list_filter = ['accepted']
    readonly_fields = ("accepted_at",)
    autocomplete_fields = ['participant', 'quiz']
    search_fields = [
        'participant__user__email',
        'quiz__title',
    ]

    # Reorder fields
    fields = [
        'participant',
        'quiz',
        'invited_at',
        'invitation_token',
        'accepted_at',
        'started_at',
        'completed_at',
        'score',
    ]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz")
    exclude = ("created_at",)
    search_fields = ['text']
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    exclude = ("created_at",)
    search_fields = ['text']


@admin.register(ParticipantAnswer)
class ParticipantAnswerAdmin(admin.ModelAdmin):
    list_display = ['participant', 'question', 'selected_choice', 'answered_at']
    list_filter = ['answered_at']
    search_fields = ['participant__user__email', 'question__text']
