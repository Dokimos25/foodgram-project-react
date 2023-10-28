from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subscriber',
    )
