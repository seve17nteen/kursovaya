from rest_framework import serializers
from .models import (
    SurveyCategory, Survey, Question, Choice,
    Response, Answer, Comment
)


class ChoiceSerializer(serializers.ModelSerializer):
    """Вариант ответа."""

    class Meta:
        model = Choice
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """Вопрос с вариантами ответов."""

    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'required', 'choices']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вопроса с вариантами."""

    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all(), write_only=True)
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['survey', 'text', 'question_type', 'order', 'required', 'choices']

    def validate(self, attrs):
        question_type = attrs.get('question_type')
        choices_data = self.initial_data.get('choices', [])

        if question_type in ('radio', 'checkbox'):
            non_empty_choices = [c for c in choices_data if c.get('text', '').strip()]
            if len(non_empty_choices) < 2:
                raise serializers.ValidationError({
                    'choices': 'Для вопросов с вариантами ответа нужно минимум 2 непустых варианта.'
                })
        return attrs

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        for choice_data in choices_data:
            if choice_data.get('text', '').strip():
                Choice.objects.create(question=question, **choice_data)
        return question


class SurveyCategorySerializer(serializers.ModelSerializer):
    """Категория опросов со счётчиком опросов."""

    surveys_count = serializers.IntegerField(
        source='surveys.count', read_only=True
    )

    class Meta:
        model = SurveyCategory
        fields = ['id', 'title', 'description', 'created_at', 'surveys_count']


class SurveyListSerializer(serializers.ModelSerializer):
    """Краткий сериализатор опроса для списка."""

    category_title = serializers.CharField(
        source='category.title', read_only=True
    )
    author_name = serializers.CharField(
        source='author.username', read_only=True
    )
    questions_count = serializers.SerializerMethodField()
    responses_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description',
            'is_published', 'is_anonymous',
            'created_at', 'views',
            'questions_count', 'responses_count',
            'category_title', 'author_name'
        ]

    def get_questions_count(self, obj):
        return getattr(obj, 'questions_count', obj.questions.count())

    def get_responses_count(self, obj):
        return getattr(obj, 'responses_count', obj.responses.count())


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор опроса с вопросами."""

    category = SurveyCategorySerializer(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.SerializerMethodField()
    responses_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description',
            'is_published', 'is_anonymous',
            'created_at', 'updated_at', 'views',
            'questions_count', 'responses_count',
            'category', 'author', 'questions'
        ]

    def get_questions_count(self, obj):
        return getattr(obj, 'questions_count', obj.questions.count())

    def get_responses_count(self, obj):
        return getattr(obj, 'responses_count', obj.responses.count())


class SurveyNestedQuestionCreateSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор вопроса при создании опроса."""

    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['text', 'question_type', 'order', 'required', 'choices']

    def validate(self, attrs):
        question_type = attrs.get('question_type')
        choices_data = attrs.get('choices', [])

        if question_type in ('radio', 'checkbox'):
            non_empty_choices = [c for c in choices_data if c.get('text', '').strip()]
            if len(non_empty_choices) < 2:
                raise serializers.ValidationError({
                    'choices': 'Для вопросов с вариантами ответа нужно минимум 2 непустых варианта.'
                })
        return attrs


class SurveyCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/обновления опроса."""

    id = serializers.IntegerField(read_only=True)
    questions = SurveyNestedQuestionCreateSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'category',
            'is_published', 'is_anonymous', 'questions'
        ]

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        author = self.context['request'].user
        survey = Survey.objects.create(author=author, **validated_data)

        for question_data in questions_data:
            choices_data = question_data.pop('choices', [])
            question = Question.objects.create(survey=survey, **question_data)
            for choice_data in choices_data:
                if choice_data.get('text', '').strip():
                    Choice.objects.create(question=question, **choice_data)

        return survey


class AnswerCreateSerializer(serializers.ModelSerializer):
    """Создание ответа на вопрос."""

    class Meta:
        model = Answer
        fields = ['question', 'choice', 'text']

    def validate(self, attrs):
        question = attrs['question']
        choice = attrs.get('choice')
        text = attrs.get('text')

        if question.question_type == 'text':
            if not text:
                raise serializers.ValidationError(
                    {'text': 'Текстовый ответ обязателен для данного типа вопроса'}
                )
        else:
            if not choice:
                raise serializers.ValidationError(
                    {'choice': 'Необходимо выбрать вариант ответа'}
                )
        return attrs


class AnswerSerializer(serializers.ModelSerializer):
    """Ответ на вопрос (для чтения)."""

    question_text = serializers.CharField(
        source='question.text', read_only=True
    )
    choice_text = serializers.CharField(
        source='choice.text', read_only=True, default=None
    )

    class Meta:
        model = Answer
        fields = ['id', 'question', 'question_text', 'choice',
                  'choice_text', 'text']


class ResponseCreateSerializer(serializers.Serializer):
    """Сериализатор для прохождения опроса — массив ответов."""

    answers = AnswerCreateSerializer(many=True)

    def create(self, validated_data):
        survey = validated_data['survey']
        user = validated_data['user']
        answers_data = validated_data.pop('answers')

        response = Response.objects.create(
            survey=survey,
            user=user,
            completed_at=None
        )

        for answer_data in answers_data:
            Answer.objects.create(response=response, **answer_data)

        from django.utils import timezone
        response.completed_at = timezone.now()
        response.save(update_fields=['completed_at'])
        return response


class ResponseSerializer(serializers.ModelSerializer):
    """Сессия прохождения опроса с ответами."""

    user_name = serializers.CharField(
        source='user.username', read_only=True
    )
    answers = AnswerSerializer(many=True, read_only=True)
    survey_title = serializers.CharField(
        source='survey.title', read_only=True
    )

    class Meta:
        model = Response
        fields = ['id', 'survey', 'survey_title', 'user', 'user_name',
                  'answers', 'created_at', 'completed_at']


class CommentSerializer(serializers.ModelSerializer):
    """Комментарий к опросу."""

    author_name = serializers.CharField(
        source='author.username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ['id', 'survey', 'text', 'author', 'author_name', 'created_at']
        read_only_fields = ['author']


class SurveyStatsSerializer(serializers.Serializer):
    """Статистика опроса."""

    total_responses = serializers.IntegerField()
    questions_stats = serializers.ListField()
