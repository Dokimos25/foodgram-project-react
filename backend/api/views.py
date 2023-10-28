from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from authentication.models import Subscription
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    Favorite,
    ShoppingCartItem,
)
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly, IsSameUser
from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeInSubscriptionSerializer,
    RecipeWritableSerializer,
    SubscriptionSerializer,
)
from .filters import RecipeFilter, IngredientFilter

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in [
            'list',
            'retrieve',
            'me',
            'subscriptions',
            'subscribe',
        ]:
            return UserSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return User.objects.all().prefetch_related('recipes')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action in [
            'me',
            'set_password',
            'subscriptions',
            'subscribe',
        ]:
            return [permissions.IsAuthenticated()]
        return [IsSameUser()]

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(
            subscriber=request.user
        ).select_related(
            'user',
        ).prefetch_related(
            'user__recipes',
        )

        page = self.paginate_queryset(subscriptions)

        serializer = SubscriptionSerializer(
            page,
            context=self.get_serializer_context(),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        subscriber = request.user
        user = self.get_object()
        if request.method == 'POST':
            if user == subscriber:
                return Response({
                    "errors": "Нельзя подписаться на самого себя"
                }, status=status.HTTP_400_BAD_REQUEST)
            subscription, create = Subscription.objects.get_or_create(
                user=user, subscriber=subscriber,
            )
            if not create:
                return Response(
                    {"errors": "Подписка уже оформлена"},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(
                subscription, 
                context=self.get_serializer_context()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if subscriptions := Subscription.objects.filter(
                    user=user, subscriber=subscriber):
                subscriptions.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Подписка не найдена"},
                status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().select_related(
        'author',
    ).prefetch_related(
        'ingredients', 'tags',
    )
    permission_classes = [IsAuthorOrReadOnly]
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWritableSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"errors": "Рецепт не найден"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item, created = ShoppingCartItem.objects.get_or_create(
                user=request.user,
                recipe=recipe,
            )
            if not created:
                return Response(
                    {"errors": "Рецепт уже в корзине"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = RecipeInSubscriptionSerializer(
                recipe, context=self.get_serializer_context()
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            recipe = self.get_object()
            queryset = ShoppingCartItem.objects.filter(
                user=request.user, recipe=recipe)
            if queryset.exists():
                queryset.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Рецепта нет в корзине"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        # shopping_cart = ShoppingCartItem.objects.filter(
        #     user=request.user
        # ).select_related(
        #     'recipe'
        # ).prefetch_related(
        #     'recipe__ingredients'
        # )
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user,
        ).select_related('ingredient').values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            amount=Sum('amount')
        )
        output = '\n'.join([
            f'{i["ingredient__name"]} - {i["amount"]}'
            f'{i["ingredient__measurement_unit"]}'
            for i in ingredients
        ])
        response = HttpResponse(
            output,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {"errors": "Рецепт не найден"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe,
            )
            if not created:
                return Response(
                    {"errors": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = RecipeInSubscriptionSerializer(
                recipe, context=self.get_serializer_context()
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            recipe = self.get_object()
            queryset = Favorite.objects.filter(
                user=request.user,
                recipe=recipe,
            )
            if queryset.exists():
                queryset.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )
