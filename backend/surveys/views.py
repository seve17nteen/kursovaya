from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    SurveyCategory, Survey, Question, Choice,
    Response as SurveyResponse, Answer, Comment
)
from .serializers import (
    SurveyCategorySerializer,
    SurveyListSerializer,
    SurveyDetailSerializer,
    SurveyCreateUpdateSerializer,
    QuestionSerializer,
    QuestionCreateSerializer,
    ChoiceSerializer,
    ResponseSerializer,
    ResponseCreateSerializer,
    AnswerSerializer,
    CommentSerializer,
)
from .permissions import (
    IsAuthorOrReadOnly,
    IsAuthorOfSurveyOrReadOnly,
    IsAdminOrReadOnly,
    IsOwnerOrReadOnly,
)


class SurveyCategoryViewSet(viewsets.ModelViewSet):
    """CRUD для категорий опросов (изменение — только админам)."""

    queryset = SurveyCategory.objects.annotate(
        surveys_count=Count('surveys', filter=Q(surveys__is_published=True))
    ).all()
    serializer_class = SurveyCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']


class SurveyViewSet(viewsets.ModelViewSet):
    """CRUD для опросов. Публичный просмотр, создание — авторизованным."""

    queryset = Survey.objects.filter(is_published=True).select_related(
        'category', 'author'
    ).prefetch_related('questions__choices').annotate(
        questions_count=Count('questions'),
        responses_count=Count('responses')
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'views', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SurveyListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return SurveyCreateUpdateSerializer
        return SurveyDetailSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthorOrReadOnly()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        """Увеличение счётчика просмотров."""
        survey = self.get_object()
        survey.views += 1
        survey.save(update_fields=['views'])
        return Response({'views': survey.views})

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        """Список моих опросов."""
        surveys = Survey.objects.filter(author=request.user).select_related(
            'category'
        ).annotate(
            questions_count=Count('questions'),
            responses_count=Count('responses')
        )
        page = self.paginate_queryset(surveys)
        if page is not None:
            serializer = SurveyListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SurveyListSerializer(surveys, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Статистика опроса (только для автора или админа)."""
        survey = self.get_object()
        if not (request.user.is_staff or request.user == survey.author):
            return Response(
                {'detail': 'Доступ запрещён'},
                status=status.HTTP_403_FORBIDDEN
            )

        total = SurveyResponse.objects.filter(survey=survey).count()
        questions_stats = []
        for question in survey.questions.all():
            q_stats = {
                'question_id': question.id,
                'question_text': question.text,
                'question_type': question.question_type,
            }
            if question.question_type in ('radio', 'checkbox'):
                choices_stats = []
                for choice in question.choices.all():
                    count = Answer.objects.filter(
                        question=question, choice=choice
                    ).count()
                    pct = round(count / total * 100, 1) if total > 0 else 0
                    choices_stats.append({
                        'choice_id': choice.id,
                        'choice_text': choice.text,
                        'count': count,
                        'percentage': pct
                    })
                q_stats['choices'] = choices_stats
            else:
                # Для текстовых — список ответов
                texts = list(Answer.objects.filter(
                    question=question
                ).exclude(text='').values_list('text', flat=True))
                q_stats['text_answers'] = texts
                q_stats['text_count'] = len(texts)
            questions_stats.append(q_stats)

        return Response({
            'survey_id': survey.id,
            'survey_title': survey.title,
            'total_responses': total,
            'questions_stats': questions_stats,
        })

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def submit_response(self, request, pk=None):
        """Отправка ответов на опрос."""
        survey = self.get_object()

        # Проверка, что опрос ещё не пройден этим пользователем
        # (разрешаем повторное прохождение, если не запрещено)

        serializer = ResponseCreateSerializer(
            data={'answers': request.data.get('answers', [])}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_obj = SurveyResponse.objects.create(
            survey=survey, user=request.user, completed_at=None
        )
        for answer_data in serializer.validated_data['answers']:
            Answer.objects.create(response=response_obj, **answer_data)

        response_obj.completed_at = timezone.now()
        response_obj.save(update_fields=['completed_at'])

        return Response(
            {'detail': 'Опрос успешно пройден', 'response_id': response_obj.id},
            status=status.HTTP_201_CREATED
        )


class QuestionViewSet(viewsets.ModelViewSet):
    """Управление вопросами опроса."""

    queryset = Question.objects.prefetch_related('choices').all()
    permission_classes = [IsAuthorOfSurveyOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return QuestionCreateSerializer
        return QuestionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        survey_id = self.request.query_params.get('survey', None)
        if survey_id:
            queryset = queryset.filter(survey_id=survey_id)
        return queryset

    def perform_create(self, serializer):
        survey_id = self.request.data.get('survey')
        survey = Survey.objects.get(pk=survey_id)
        if survey.author != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('Вы не автор этого опроса')
        serializer.save(survey=survey)


class ChoiceViewSet(viewsets.ModelViewSet):
    """Управление вариантами ответов."""

    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthorOfSurveyOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        question_id = self.request.query_params.get('question', None)
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        return queryset


class ResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр ответов на опросы."""

    queryset = SurveyResponse.objects.select_related(
        'survey', 'user'
    ).prefetch_related('answers__question', 'answers__choice')
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Пользователь видит только свои ответы
            queryset = queryset.filter(user=self.request.user)
        survey_id = self.request.query_params.get('survey', None)
        if survey_id:
            queryset = queryset.filter(survey_id=survey_id)
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    """Комментарии к опросам."""

    queryset = Comment.objects.select_related('author').all()
    serializer_class = CommentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwnerOrReadOnly()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        survey_id = self.request.query_params.get('survey', None)
        if survey_id:
            queryset = queryset.filter(survey_id=survey_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
