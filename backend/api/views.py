from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientsFilter, RecipesFilter
from api.mixins import CustomViewMixin
from api.pagination import Paginator
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    CreateRecipeSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    ShoppingCartSerializer,
    FollowSerializer,
    GetRecipeSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Follow, User


class TagViewSet(CustomViewMixin):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)


class IngredientViewSet(CustomViewMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = IngredientsFilter


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = Paginator
    lookup_field = 'username'

    @action(detail=True, methods=('POST', 'DELETE'))
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            folllowing = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(folllowing,
                                          context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        folllowing = get_object_or_404(Follow, user=user, author=author)
        folllowing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def subscriptions(self, request):
        folllowing = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(folllowing)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    pagination_class = Paginator
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return CreateRecipeSerializer

    @action(detail=True, methods=('POST',))
    def shopping_cart(self, request, pk):
        return self._add_recipe(request, pk, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        get_object_or_404(ShoppingCart,
                          recipe__id=pk,
                          user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST',))
    def favorite(self, request, pk):
        return self._add_recipe(request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk):
        get_object_or_404(Favorite,
                          recipe=get_object_or_404(Recipe, id=pk),
                          user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(amount=Sum('amount'))

        shopping_cart_data = [
            f"{item['ingredient__name']} - "
            f"{item['ingredient__measurement_unit']} | "
            f"{item['amount']}"
            for item in ingredients
        ]
        shopping_cart_text = '\n'.join(shopping_cart_data)

        file = 'shopping_cart_list.txt'
        headers = {'Content-Disposition': (f'attachment; filename={file}')}
        return HttpResponse(shopping_cart_text,
                            content_type='text/plain; charset=UTF-8',
                            headers=headers)

    def _add_recipe(self, request, pk, serializer_class):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer_class(
            data={'recipe': recipe.id, 'user': request.user.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
