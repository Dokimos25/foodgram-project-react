from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

from authentication.models import User, Subscription
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    Favorite,
    ShoppingCartItem,
)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous or user == obj:
            return False
        return Subscription.objects.filter(
            user=obj, subscriber=user).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class IngredientInRecipeWritableSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set',
        many=True
    )
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCartItem.objects.filter(
            user=user,
            recipe=obj,
        ).exists()


class RecipeWritableSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientInRecipeWritableSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients]
        )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=instance,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients]
        )
        return instance

    def validate_image(self, value):
        if not value:
            raise ValidationError('Изображение не выбрано')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Нужен хотя бы один ингредиент')
        ingredient_ids = [ingredient['id'] for ingredient in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Ингредиенты не должны повторяться')
        for ingredient in value:
            if ingredient['amount'] <= 0:
                raise ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
            if Ingredient.objects.filter(pk=ingredient['id']).exists():
                continue
            raise ValidationError('Такого ингредиента не существует')
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Нужен хотя бы один тег')
        tag_ids = [tag.id for tag in value]
        if len(tag_ids) != len(set(tag_ids)):
            raise ValidationError('Теги не должны повторяться')
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class RecipeInSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.user.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.user.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeInSubscriptionSerializer(recipes, many=True).data
