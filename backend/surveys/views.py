from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Answer,
    Choice,
    Comment,
    Question,
    Response as SurveyResponse,
    Survey,
    SurveyCategory,
)
from .permissions import (
    IsAdminOrReadOnly,
    IsAuthorOfSurveyOrReadOnly,
    IsAuthorOrReadOnly,
    IsOwnerOrReadOnly,
)
from .serializers import (
    ChoiceSerializer,
    CommentSerializer,
    QuestionCreateSerializer,
    QuestionSerializer,
    ResponseCreateSerializer,
    ResponseSerializer,
    SurveyCategorySerializer,
    SurveyCreateUpdateSerializer,
    SurveyDetailSerializer,
    SurveyListSerializer,
)


class SurveyCategoryViewSet(viewsets.ModelViewSet):
    """CRUD для категорий опросов (изменение — только админам)."""

    queryset = SurveyCategory.objects.all()
    serializer_class = SurveyCategorySerializer

    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        SurveyCategory.objects.get_or_create(
            title='Другое',
            defaults={
                'description': 'Категория для опросов, которым не подошли стандартные категории.'
            }
        )
        return SurveyCategory.objects.annotate(
            surveys_count=Count('surveys', filter=Q(surveys__is_published=True))
        ).order_by('title')


class SurveyViewSet(viewsets.ModelViewSet):
    """CRUD для опросов. Публичный просмотр, создание — авторизованным."""

    queryset = Survey.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'views', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Survey.objects.filter(is_published=True).select_related(
            'category', 'author'
        ).prefetch_related('questions__choices').annotate(
            questions_count=Count('questions'),
            responses_count=Count('responses')
        )
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return SurveyListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return SurveyCreateUpdateSerializer
        return SurveyDetailSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthorOrReadOnly()]
        if self.action in ('create', 'submit_response', 'my'):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        survey = self.get_object()
        survey.views += 1
        survey.save(update_fields=['views'])
        return Response({'views': survey.views})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
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
        survey = self.get_object()
        if not request.user.is_authenticated or not (
            request.user.is_staff or request.user == survey.author
        ):
            return Response({'detail': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

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
                    count = Answer.objects.filter(question=question, choice=choice).count()
                    pct = round(count / total * 100, 1) if total > 0 else 0
                    choices_stats.append({
                        'choice_id': choice.id,
                        'choice_text': choice.text,
                        'count': count,
                        'percentage': pct,
                    })
                q_stats['choices'] = choices_stats
            else:
                texts = list(
                    Answer.objects.filter(question=question)
                    .exclude(text='')
                    .values_list('text', flat=True)
                )
                q_stats['text_answers'] = texts
                q_stats['text_count'] = len(texts)
            questions_stats.append(q_stats)

        return Response({
            'survey_id': survey.id,
            'survey_title': survey.title,
            'total_responses': total,
            'questions_stats': questions_stats,
        })

    @action(detail=True, methods=['post'])
    def submit_response(self, request, pk=None):
        survey = self.get_object()

        if SurveyResponse.objects.filter(survey=survey, user=request.user).exists():
            return Response({'detail': 'Вы уже проходили этот опрос'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResponseCreateSerializer(data={'answers': request.data.get('answers', [])})
        serializer.is_valid(raise_exception=True)

        response_obj = SurveyResponse.objects.create(
            survey=survey,
            user=request.user,
            completed_at=timezone.now(),
        )
        for answer_data in serializer.validated_data['answers']:
            Answer.objects.create(response=response_obj, **answer_data)

        return Response(
            {'detail': 'Опрос успешно пройден', 'response_id': response_obj.id},
            status=status.HTTP_201_CREATED,
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
        survey_id = self.request.query_params.get('survey')
        if survey_id:
            queryset = queryset.filter(survey_id=survey_id)
        return queryset

    def perform_create(self, serializer):
        survey = serializer.validated_data['survey']
        if survey.author != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('Вы не автор этого опроса')
        serializer.save()


class ChoiceViewSet(viewsets.ModelViewSet):
    """Управление вариантами ответов."""

    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthorOfSurveyOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        question_id = self.request.query_params.get('question')
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        return queryset


class ResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр ответов на опросы."""

    queryset = SurveyResponse.objects.select_related('survey', 'user').prefetch_related(
        'answers__question', 'answers__choice'
    )
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        survey_id = self.request.query_params.get('survey')
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
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        survey_id = self.request.query_params.get('survey')
        if survey_id:
            queryset = queryset.filter(survey_id=survey_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
