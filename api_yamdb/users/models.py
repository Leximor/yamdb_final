from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = (
    ('admin', 'администратор'),
    ('moderator', 'Модератор'),
    ('user', 'Аутентифицированный пользователь'),
)
USERNAME = 'username'


class UserRole(Enum):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    ROLES = ROLES
    email = models.EmailField('Почта', unique=True)
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField(
        'Роль', max_length=50, choices=ROLES, default='user',)

    class Meta:
        ordering = [USERNAME]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
