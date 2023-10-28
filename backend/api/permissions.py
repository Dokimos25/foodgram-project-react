from rest_framework.permissions import (BasePermission,
                                        SAFE_METHODS,
                                        IsAuthenticatedOrReadOnly)


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsSameUser(BasePermission):
    # def has_permission(self, request, view):
    #     return request.user.is_authenticated
    # or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj == request.user
