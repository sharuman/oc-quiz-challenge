from django.contrib import admin
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
    list_display = ('email', 'full_name', 'created_at', 'updated_at')
    search_fields = ['user__email']

    def email(self, obj):
        return obj.user.email

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "created_at")
    exclude = ("created_at",)
    readonly_fields = ("creator",)
    search_fields = ['title']
    inlines = [QuestionInline]

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
