from django.contrib import admin
from .models import SurveyCategory, Survey, Question, Choice, Response, Answer, Comment


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('text', 'question_type', 'order', 'required')
    ordering = ('order',)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1
    fields = ('text', 'order')
    ordering = ('order',)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ('question', 'choice', 'text')
    readonly_fields = ('question', 'choice', 'text')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SurveyCategory)
class SurveyCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    ordering = ('title',)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'author',
        'is_published', 'is_anonymous', 'responses_count',
        'created_at', 'views'
    )
    list_display_links = ('id', 'title')
    list_filter = ('is_published', 'category', 'is_anonymous')
    search_fields = ('title', 'description')
    list_editable = ('is_published',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    inlines = [QuestionInline]

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title', 'description', 'category',
                'author', 'is_published', 'is_anonymous'
            )
        }),
        ('Статистика', {
            'fields': ('views', 'created_at', 'updated_at')
        }),
    )

    def responses_count(self, obj):
        return obj.responses_count
    responses_count.short_description = 'Ответов'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'text_short', 'question_type', 'order', 'required')
    list_display_links = ('id',)
    list_filter = ('question_type', 'required', 'survey')
    search_fields = ('text', 'survey__title')
    inlines = [ChoiceInline]

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'Текст'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'question', 'order')
    list_display_links = ('id', 'text')
    list_filter = ('question__survey',)
    search_fields = ('text', 'question__text')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'user', 'created_at', 'completed_at')
    list_display_links = ('id',)
    list_filter = ('survey', 'created_at')
    search_fields = ('user__username', 'survey__title')
    readonly_fields = ('created_at',)
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'response', 'question_short', 'choice', 'text_short')
    list_display_links = ('id',)
    search_fields = ('text', 'choice__text', 'question__text')

    def question_short(self, obj):
        return obj.question.text[:60]
    question_short.short_description = 'Вопрос'

    def text_short(self, obj):
        return obj.text[:60] if obj.text else '-'
    text_short.short_description = 'Текст'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'author', 'text_short', 'created_at')
    list_display_links = ('id',)
    list_filter = ('survey', 'created_at')
    search_fields = ('text', 'author__username', 'survey__title')

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'Текст'
