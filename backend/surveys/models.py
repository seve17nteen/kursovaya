from django.db import models
from django.conf import settings


class SurveyCategory(models.Model):
    """Категория опросов (образование, технологии, здоровье и т.д.)."""

    title = models.CharField(
        max_length=150,
        db_index=True,
        verbose_name='Название категории'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория опроса'
        verbose_name_plural = 'Категории опросов'
        ordering = ['title']


class Survey(models.Model):
    """Опрос / анкета."""

    title = models.CharField(
        max_length=200,
        verbose_name='Название опроса'
    )
    description = models.TextField(
        verbose_name='Описание опроса'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликован'
    )
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name='Анонимный опрос'
    )
    views = models.PositiveIntegerField(
        default=0,
        verbose_name='Просмотры'
    )
    category = models.ForeignKey(
        SurveyCategory,
        on_delete=models.PROTECT,
        related_name='surveys',
        verbose_name='Категория'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='surveys',
        verbose_name='Автор'
    )

    def __str__(self):
        return self.title

    @property
    def questions_count(self):
        return self.questions.count()

    @property
    def responses_count(self):
        return self.responses.count()

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering = ['-created_at']


class Question(models.Model):
    """Вопрос внутри опроса."""

    QUESTION_TYPES = [
        ('radio', 'Один вариант'),
        ('checkbox', 'Несколько вариантов'),
        ('text', 'Текстовый ответ'),
    ]

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Опрос'
    )
    text = models.TextField(
        verbose_name='Текст вопроса'
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPES,
        default='radio',
        verbose_name='Тип вопроса'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    required = models.BooleanField(
        default=True,
        verbose_name='Обязательный'
    )

    def __str__(self):
        return f'[{self.survey.title}] {self.text[:80]}'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['survey', 'order']


class Choice(models.Model):
    """Вариант ответа на вопрос."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Вопрос'
    )
    text = models.CharField(
        max_length=300,
        verbose_name='Текст варианта'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )

    def __str__(self):
        return f'[{self.question.text[:50]}] {self.text}'

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['question', 'order']


class Response(models.Model):
    """Факт прохождения опроса пользователем."""

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Опрос'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='survey_responses',
        verbose_name='Респондент'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата начала'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата завершения'
    )

    def __str__(self):
        return f'{self.user.username} → {self.survey.title}'

    class Meta:
        verbose_name = 'Ответ на опрос'
        verbose_name_plural = 'Ответы на опросы'
        ordering = ['-created_at']
        # Один пользователь может пройти опрос несколько раз
        # unique_together не добавляем — разрешаем повторное прохождение


class Answer(models.Model):
    """Ответ пользователя на конкретный вопрос."""

    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Сессия ответа'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='answers',
        verbose_name='Выбранный вариант'
    )
    text = models.TextField(
        blank=True,
        verbose_name='Текстовый ответ'
    )

    def __str__(self):
        if self.text:
            return f'{self.question.text[:50]} → {self.text[:50]}'
        if self.choice:
            return f'{self.question.text[:50]} → {self.choice.text}'
        return f'{self.question.text[:50]} → (нет ответа)'

    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'
        # Уникальная пара: один вопрос в одной сессии — один ответ
        constraints = [
            models.UniqueConstraint(
                fields=['response', 'question'],
                name='unique_answer_per_question_per_response'
            )
        ]


class Comment(models.Model):
    """Комментарий к опросу."""

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Опрос'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f'{self.author.username}: {self.text[:60]}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
