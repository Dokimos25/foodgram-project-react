from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from recipes.models import Tag, Ingredient, Recipe

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    """
    Фильтр по ингредиентам
    """
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """
    Фильтр по рецептам
    """
    author = filters.ModelChoiceFilter(
        field_name='author',
        queryset=User.objects.all(),
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(favorites__user=self.request.user)
            return queryset.exclude(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=self.request.user)
            return queryset.exclude(shopping_cart__user=self.request.user)
        return queryset
