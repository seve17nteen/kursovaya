from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Расширенная модель пользователя."""

    bio = models.TextField(verbose_name='О себе', blank=True)
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d',
        verbose_name='Аватар',
        blank=True
    )
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
