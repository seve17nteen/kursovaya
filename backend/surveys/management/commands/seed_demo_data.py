from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from surveys.models import (
    SurveyCategory,
    Survey,
    Question,
    Choice,
    Comment,
    Response,
    Answer,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт демонстрационные данные: пользователи, категории, опросы, комментарии и ответы'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Создание seed-данных...'))

        # Users
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User',
            }
        )
        if admin_created:
            admin_user.set_password('AdminPass123!')
            admin_user.save()

        anna, _ = User.objects.get_or_create(
            username='anna',
            defaults={
                'email': 'anna@example.com',
                'first_name': 'Анна',
                'last_name': 'Смирнова',
                'bio': 'Маркетолог и исследователь пользовательского опыта.',
                'phone': '+79990000001',
            }
        )
        anna.set_password('UserPass123!')
        anna.save()

        ivan, _ = User.objects.get_or_create(
            username='ivan',
            defaults={
                'email': 'ivan@example.com',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'bio': 'Frontend-разработчик, любит проводить внутренние опросы.',
                'phone': '+79990000002',
            }
        )
        ivan.set_password('UserPass123!')
        ivan.save()

        maria, _ = User.objects.get_or_create(
            username='maria',
            defaults={
                'email': 'maria@example.com',
                'first_name': 'Мария',
                'last_name': 'Кузнецова',
                'bio': 'HR-специалист, собирает обратную связь сотрудников.',
                'phone': '+79990000003',
            }
        )
        maria.set_password('UserPass123!')
        maria.save()

        # Categories
        education, _ = SurveyCategory.objects.get_or_create(
            title='Образование',
            defaults={'description': 'Опросы об учебном процессе и образовательных сервисах.'}
        )
        tech, _ = SurveyCategory.objects.get_or_create(
            title='Технологии',
            defaults={'description': 'Опросы о технологиях, инструментах и разработке.'}
        )
        hr, _ = SurveyCategory.objects.get_or_create(
            title='HR и команда',
            defaults={'description': 'Опросы о команде, вовлечённости и внутренних процессах.'}
        )
        lifestyle, _ = SurveyCategory.objects.get_or_create(
            title='Образ жизни',
            defaults={'description': 'Опросы о привычках, интересах и досуге.'}
        )
        business, _ = SurveyCategory.objects.get_or_create(
            title='Бизнес',
            defaults={'description': 'Опросы о бизнесе, продуктах, клиентах и продажах.'}
        )
        marketing, _ = SurveyCategory.objects.get_or_create(
            title='Маркетинг',
            defaults={'description': 'Опросы о рекламе, бренде, аудитории и продвижении.'}
        )
        health, _ = SurveyCategory.objects.get_or_create(
            title='Здоровье',
            defaults={'description': 'Опросы о самочувствии, привычках и здоровье.'}
        )
        entertainment, _ = SurveyCategory.objects.get_or_create(
            title='Развлечения',
            defaults={'description': 'Опросы о фильмах, музыке, играх и досуге.'}
        )
        science, _ = SurveyCategory.objects.get_or_create(
            title='Наука',
            defaults={'description': 'Опросы о научных интересах, исследованиях и образовании.'}
        )
        society, _ = SurveyCategory.objects.get_or_create(
            title='Общество',
            defaults={'description': 'Опросы о социальных привычках, мнениях и общественных темах.'}
        )
        travel, _ = SurveyCategory.objects.get_or_create(
            title='Путешествия',
            defaults={'description': 'Опросы о поездках, маршрутах и туристических сервисах.'}
        )
        sport, _ = SurveyCategory.objects.get_or_create(
            title='Спорт',
            defaults={'description': 'Опросы о спорте, активности и тренировках.'}
        )
        other, _ = SurveyCategory.objects.get_or_create(
            title='Другое',
            defaults={'description': 'Категория для опросов, которым не подошли стандартные категории.'}
        )

        # Survey 1
        survey1, _ = Survey.objects.get_or_create(
            title='Оценка качества онлайн-курсов',
            defaults={
                'description': 'Анкета для студентов по качеству онлайн-обучения, платформы и контента.',
                'category': education,
                'author': anna,
                'is_published': True,
                'is_anonymous': False,
                'views': 18,
            }
        )
        if not survey1.questions.exists():
            q1 = Question.objects.create(
                survey=survey1,
                text='Насколько удобно вам пользоваться платформой онлайн-курсов?',
                question_type='radio',
                order=1,
                required=True,
            )
            c11 = Choice.objects.create(question=q1, text='Очень удобно', order=1)
            c12 = Choice.objects.create(question=q1, text='Скорее удобно', order=2)
            c13 = Choice.objects.create(question=q1, text='Скорее неудобно', order=3)
            c14 = Choice.objects.create(question=q1, text='Очень неудобно', order=4)

            q2 = Question.objects.create(
                survey=survey1,
                text='Какие элементы платформы вам нравятся больше всего?',
                question_type='checkbox',
                order=2,
                required=False,
            )
            Choice.objects.create(question=q2, text='Дизайн интерфейса', order=1)
            Choice.objects.create(question=q2, text='Скорость работы', order=2)
            Choice.objects.create(question=q2, text='Структура курсов', order=3)
            Choice.objects.create(question=q2, text='Тесты и задания', order=4)

            q3 = Question.objects.create(
                survey=survey1,
                text='Что бы вы улучшили в платформе?',
                question_type='text',
                order=3,
                required=False,
            )

            response = Response.objects.create(
                survey=survey1,
                user=ivan,
                completed_at=timezone.now(),
            )
            Answer.objects.create(response=response, question=q1, choice=c12)
            Answer.objects.create(response=response, question=q2, choice=q2.choices.first())
            Answer.objects.create(response=response, question=q3, text='Добавил бы больше интерактивных заданий и быстрый поиск по курсам.')

        # Survey 2
        survey2, _ = Survey.objects.get_or_create(
            title='Использование React в учебных и рабочих проектах',
            defaults={
                'description': 'Опрос для разработчиков о том, как они применяют React и связанные инструменты.',
                'category': tech,
                'author': ivan,
                'is_published': True,
                'is_anonymous': False,
                'views': 27,
            }
        )
        if not survey2.questions.exists():
            q1 = Question.objects.create(
                survey=survey2,
                text='Используете ли вы React в реальных проектах?',
                question_type='radio',
                order=1,
                required=True,
            )
            c21 = Choice.objects.create(question=q1, text='Да, постоянно', order=1)
            c22 = Choice.objects.create(question=q1, text='Иногда', order=2)
            c23 = Choice.objects.create(question=q1, text='Пока только изучаю', order=3)

            q2 = Question.objects.create(
                survey=survey2,
                text='Какие библиотеки вы обычно используете вместе с React?',
                question_type='checkbox',
                order=2,
                required=False,
            )
            Choice.objects.create(question=q2, text='React Router', order=1)
            Choice.objects.create(question=q2, text='Axios', order=2)
            Choice.objects.create(question=q2, text='Redux Toolkit', order=3)
            Choice.objects.create(question=q2, text='React Query', order=4)

            q3 = Question.objects.create(
                survey=survey2,
                text='Какой совет вы дали бы новичку в React?',
                question_type='text',
                order=3,
                required=False,
            )

            response = Response.objects.create(
                survey=survey2,
                user=maria,
                completed_at=timezone.now(),
            )
            Answer.objects.create(response=response, question=q1, choice=c23)
            Answer.objects.create(response=response, question=q2, choice=q2.choices.first())
            Answer.objects.create(response=response, question=q3, text='Сначала понять компоненты, props, state и только потом лезть в сложные библиотеки.')

        # Survey 3
        survey3, _ = Survey.objects.get_or_create(
            title='Удовлетворённость внутренними процессами команды',
            defaults={
                'description': 'Опрос сотрудников о коммуникации, процессах и атмосфере в команде.',
                'category': hr,
                'author': maria,
                'is_published': True,
                'is_anonymous': True,
                'views': 14,
            }
        )
        if not survey3.questions.exists():
            q1 = Question.objects.create(
                survey=survey3,
                text='Насколько вы довольны текущими процессами коммуникации?',
                question_type='radio',
                order=1,
                required=True,
            )
            c31 = Choice.objects.create(question=q1, text='Полностью доволен', order=1)
            c32 = Choice.objects.create(question=q1, text='Скорее доволен', order=2)
            c33 = Choice.objects.create(question=q1, text='Скорее недоволен', order=3)

            q2 = Question.objects.create(
                survey=survey3,
                text='Какие направления стоит улучшить?',
                question_type='checkbox',
                order=2,
                required=False,
            )
            Choice.objects.create(question=q2, text='Постановка задач', order=1)
            Choice.objects.create(question=q2, text='Обратная связь', order=2)
            Choice.objects.create(question=q2, text='Онбординг', order=3)
            Choice.objects.create(question=q2, text='Планирование спринтов', order=4)

            q3 = Question.objects.create(
                survey=survey3,
                text='Ваши предложения по улучшению процессов',
                question_type='text',
                order=3,
                required=False,
            )

        # Survey 4
        survey4, _ = Survey.objects.get_or_create(
            title='Привычки цифрового досуга',
            defaults={
                'description': 'Исследование предпочтений пользователей в цифровом досуге: фильмы, игры, соцсети.',
                'category': lifestyle,
                'author': anna,
                'is_published': True,
                'is_anonymous': False,
                'views': 9,
            }
        )
        if not survey4.questions.exists():
            q1 = Question.objects.create(
                survey=survey4,
                text='Сколько времени в день вы проводите в интернете для отдыха?',
                question_type='radio',
                order=1,
                required=True,
            )
            c41 = Choice.objects.create(question=q1, text='Менее 1 часа', order=1)
            c42 = Choice.objects.create(question=q1, text='1–3 часа', order=2)
            c43 = Choice.objects.create(question=q1, text='Более 3 часов', order=3)

            q2 = Question.objects.create(
                survey=survey4,
                text='Что вы выбираете чаще всего?',
                question_type='checkbox',
                order=2,
                required=False,
            )
            Choice.objects.create(question=q2, text='Фильмы и сериалы', order=1)
            Choice.objects.create(question=q2, text='Игры', order=2)
            Choice.objects.create(question=q2, text='Социальные сети', order=3)
            Choice.objects.create(question=q2, text='Подкасты', order=4)

            q3 = Question.objects.create(
                survey=survey4,
                text='Какой цифровой сервис вы бы порекомендовали друзьям?',
                question_type='text',
                order=3,
                required=False,
            )

            response = Response.objects.create(
                survey=survey4,
                user=ivan,
                completed_at=timezone.now(),
            )
            Answer.objects.create(response=response, question=q1, choice=c42)
            Answer.objects.create(response=response, question=q2, choice=q2.choices.first())
            Answer.objects.create(response=response, question=q3, text='YouTube — как источник обучения и развлечения одновременно.')

        # Comments
        comments_data = [
            (survey1, maria, 'Очень полезная анкета, вопросы сформулированы понятно.'),
            (survey2, anna, 'Интересный опрос, особенно понравился блок про библиотеки.'),
            (survey2, maria, 'Хотелось бы ещё вопрос про TypeScript и тестирование.'),
            (survey3, ivan, 'Хорошо, что можно анонимно оставить мнение о процессах.'),
            (survey4, anna, 'Любопытно будет посмотреть на итоговую статистику по досугу.'),
        ]

        for survey, author, text in comments_data:
            Comment.objects.get_or_create(
                survey=survey,
                author=author,
                text=text,
            )

        self.stdout.write(self.style.SUCCESS('Seed-данные успешно созданы.'))
        self.stdout.write('Пользователи: admin / anna / ivan / maria')
        self.stdout.write('Пароли: admin = AdminPass123!, остальные = UserPass123!')
