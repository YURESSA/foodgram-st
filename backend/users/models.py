from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from constants import (
    USER_IMAGE_UPLOAD_PATH,
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
)


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        verbose_name='Электронная почта',
    )
    username = models.CharField(
        unique=True,
        max_length=MAX_USERNAME_LENGTH,
        verbose_name='Логин',
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Фамилия',
    )
    profile_image = models.ImageField(
        upload_to=USER_IMAGE_UPLOAD_PATH,
        null=True,
        blank=True,
        verbose_name='Фотография профиля',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return f'{self.username} ({self.email})'


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_set',
        verbose_name='Пользователь-читатель',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_set',
        verbose_name='Пользователь-автор',
    )
    followed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время подписки',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Список подписок'
        ordering = ['-followed_at']
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='no_duplicate_follows'
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.follower} подписан {self.following}'
