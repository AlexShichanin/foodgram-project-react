import re

from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название', unique=True, max_length=200)
    color = models.CharField(
        'HEX-цвет',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#(?:[A-Fa-f0-9]{3}){1,2}$',
                message='Введите HEX-код в формате #AAF123 или #333',
                flags=re.IGNORECASE)
        ])
    slug = models.SlugField('SLUG', unique=True, max_length=200)

    def validate_unique_name(self, name_lower):
        if self.__class__.objects.filter(
                name__iexact=name_lower).exclude(pk=self.pk).exists():
            raise ValidationError('Тег с таким названием уже существует!')

    def validate_unique_color(self, color_lower):
        if self.__class__.objects.filter(
                color__iexact=color_lower).exclude(pk=self.pk).exists():
            raise ValidationError('Тег с таким HEX-кодом уже существует!')

    def validate_unique_slug(self, slug_lower):
        if self.__class__.objects.filter(
                slug__iexact=slug_lower).exclude(pk=self.pk).exists():
            raise ValidationError('Тег с таким SLUG уже существует!')

    def clean(self):
        name = self.name.lower()
        color = self.color.lower()
        slug = self.slug.lower()

        self.validate_unique_name(name)
        self.validate_unique_color(color)
        self.validate_unique_slug(slug)

    def save(self, *args, **kwargs):
        self.color = self.color.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='unique_name_color')
        ]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient')
        ]

    def __str__(self):
        return (f'{self.name} - {self.measurement_unit}')


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200, unique=True)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное время приготовления 1 минута'),
            MaxValueValidator(
                720,
                message='Максимальное время приготовления 12 часов')
        ])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное количество ингредиентов 1'),
            MaxValueValidator(
                100,
                message='Максимальное количество ингредиентов 100')
        ])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_ingredient_in_recipe')]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class FavoriteAndShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='%(app_label)s_%(class)s_unique')
        ]


class ShoppingCart(FavoriteAndShoppingCart):
    class Meta(FavoriteAndShoppingCart.Meta):
        default_related_name = 'shopping_carts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe.name} в список покупок'


class Favorite(FavoriteAndShoppingCart):
    class Meta(FavoriteAndShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил {self.recipe.name} в избранное'
