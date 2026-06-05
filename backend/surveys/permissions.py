from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его автору.
    Чтение доступно всем.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthorOfSurveyOrReadOnly(permissions.BasePermission):
    """
    Для действий с вопросом/вариантом: проверяем автора родительского опроса.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Question → survey.author, Choice → question.survey.author
        if hasattr(obj, 'survey'):
            return obj.survey.author == request.user
        if hasattr(obj, 'question'):
            return obj.question.survey.author == request.user
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее изменять данные только администраторам.
    Чтение доступно всем.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение для ответов (Response): только владелец может видеть/удалять.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user or request.user.is_staff
        return obj.user == request.user
