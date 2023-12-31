from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    def clean(self):
        if self.user == self.author:
            raise ValidationError("Самоподписка запрещено!")

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following')
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
