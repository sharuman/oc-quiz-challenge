from django.contrib import admin
from .models import Choice, Participant, Question, Quiz, QuizParticipant


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
    list_filter = ['accepted']
    autocomplete_fields = ['participant', 'quiz']

    # Reorder fields
    fields = [
        'participant',
        'quiz',
        'invited_at',
        'invitation_token',
        'accepted',
        'started_at',
        'submitted_at',
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

