from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

# Получаем вашу кастомную модель User
User = get_user_model()


class LoginOrEmailBackend(ModelBackend):
    """
    Аутентификационный бэкенд, позволяющий пользователю входить
    с помощью логина (USERNAME_FIELD) ИЛИ email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Поле username здесь содержит то, что ввел пользователь: логин или почту

        try:
            # Используем Q-объекты для построения OR-запроса:
            # Ищем пользователя, у которого login=username ИЛИ email=username
            user = User.objects.get(
                Q(login=username) | Q(email=username)
            )
        except User.DoesNotExist:
            # Если пользователь не найден ни по логину, ни по почте,
            # возвращаем None, сообщая Django, что аутентификация не удалась
            return None

        # Если пользователь найден, проверяем его пароль
        if user.check_password(password):
            # check_password - это метод AbstractBaseUser, который проверяет
            # введенный пароль на соответствие хешу в БД
            return user

        return None

    # Этот метод обязателен для работы с разрешениями
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None