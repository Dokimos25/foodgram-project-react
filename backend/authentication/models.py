from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )

    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    USERNAME_FIELD = 'email'


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscribers'
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriptions'
    )

    def clean(self):
        if self.user.id == self.subscriber.id:
            raise ValidationError(
                message='Нельзя подписаться на самого себя'
            )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscriber'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
