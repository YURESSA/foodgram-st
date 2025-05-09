from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                pattern=r'^[\w.@+-]+$',
                message="Можно использовать только буквы, цифры и символы @/./+/-/_"
            )
        ]
    )
    first_name = models.CharField(
        "Имя",
        max_length=150
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=150
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True
    )
    profile_picture = models.ImageField(
        "Фотография профиля",
        upload_to="user_avatars/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        "Дата регистрации",
        auto_now_add=True
    )

    class Meta:
        ordering = ["-username"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
