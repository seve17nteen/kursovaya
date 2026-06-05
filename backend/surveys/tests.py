from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import SurveyCategory, Survey, Question, Choice, Comment

User = get_user_model()


class SurveyModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='StrongPass123!'
        )
        self.category = SurveyCategory.objects.create(
            title='Технологии',
            description='Опросы про технологии'
        )
        self.survey = Survey.objects.create(
            title='Опрос по React',
            description='Проверка знаний React',
            category=self.category,
            author=self.user,
        )
        self.question = Question.objects.create(
            survey=self.survey,
            text='Используете ли вы React?',
            question_type='radio',
            order=1,
            required=True,
        )
        self.choice_yes = Choice.objects.create(
            question=self.question,
            text='Да',
            order=1,
        )
        self.choice_no = Choice.objects.create(
            question=self.question,
            text='Нет',
            order=2,
        )

    def test_survey_str(self):
        self.assertEqual(str(self.survey), 'Опрос по React')

    def test_question_str_contains_survey_title(self):
        self.assertIn('Опрос по React', str(self.question))

    def test_survey_has_one_question(self):
        self.assertEqual(self.survey.questions.count(), 1)


class SurveyAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='StrongPass123!'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPass123!'
        )
        self.category = SurveyCategory.objects.create(
            title='Образование',
            description='Учебные опросы'
        )
        self.survey = Survey.objects.create(
            title='Тестовый опрос',
            description='Описание тестового опроса',
            category=self.category,
            author=self.user,
        )
        self.question = Question.objects.create(
            survey=self.survey,
            text='Любите Django?',
            question_type='radio',
            order=1,
            required=True,
        )
        self.choice = Choice.objects.create(
            question=self.question,
            text='Да',
            order=1,
        )

    def authenticate(self, user):
        response = self.client.post(
            '/api/auth/login/',
            {'username': user.username, 'password': 'StrongPass123!'},
            format='json'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_get_surveys_list(self):
        response = self.client.get('/api/surveys/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_authenticated_user_can_create_survey(self):
        self.authenticate(self.user)
        payload = {
            'title': 'Новый опрос',
            'description': 'Описание',
            'category': self.category.id,
            'is_published': True,
            'is_anonymous': False,
            'questions': [
                {
                    'text': 'Первый вопрос?',
                    'question_type': 'radio',
                    'order': 1,
                    'required': True,
                    'choices': [
                        {'text': 'Да', 'order': 1},
                        {'text': 'Нет', 'order': 2},
                    ]
                }
            ]
        }
        response = self.client.post('/api/surveys/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.filter(title='Новый опрос').count(), 1)
        self.assertEqual(Survey.objects.get(title='Новый опрос').questions.count(), 1)

    def test_submit_response_requires_auth(self):
        response = self.client.post(
            f'/api/surveys/{self.survey.id}/submit_response/',
            {'answers': [{'question': self.question.id, 'choice': self.choice.id}]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_comment(self):
        self.authenticate(self.other_user)
        payload = {
            'survey': self.survey.id,
            'text': 'Отличный опрос!',
        }
        response = self.client.post('/api/comments/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().author, self.other_user)

    def test_user_cannot_vote_twice(self):
        self.authenticate(self.other_user)
        payload = {
            'answers': [{'question': self.question.id, 'choice': self.choice.id}]
        }
        first_response = self.client.post(
            f'/api/surveys/{self.survey.id}/submit_response/',
            payload,
            format='json'
        )
        second_response = self.client.post(
            f'/api/surveys/{self.survey.id}/submit_response/',
            payload,
            format='json'
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.data['detail'], 'Вы уже проходили этот опрос')

    def test_author_can_view_stats(self):
        self.authenticate(self.user)
        response = self.client.get(f'/api/surveys/{self.survey.id}/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_responses', response.data)
        self.assertIn('questions_stats', response.data)
