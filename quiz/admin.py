from django.contrib import admin
from .models import Quiz, Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    exclude = ("created_at",)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    exclude = ("created_at",)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "created_at")
    exclude = ("created_at",)
    readonly_fields = ("creator",)  # Hide it from the form
    inlines = [QuestionInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.save()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz")
    exclude = ("created_at",)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    exclude = ("created_at",)

