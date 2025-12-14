from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


# 1. Создаем кастомный менеджер
class CustomUserManager(BaseUserManager):
    # Метод для создания обычного пользователя
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('The Login field must be set')

        # Можете использовать login как USERNAME_FIELD
        user = self.model(login=login, **extra_fields)

        # Хеширование пароля
        user.set_password(password)

        user.save(using=self._db)
        return user

    # Метод для создания суперпользователя
    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(login, password, **extra_fields)


# 2. Создаем кастомную модель пользователя
class User(AbstractBaseUser, PermissionsMixin):
    # Поле, которое вы используете для входа (логин)
    login = models.CharField(max_length=40, unique=True, db_index=True)

    # Поля, которые вы использовали ранее
    email = models.EmailField(max_length=40, unique=True, null=True, blank=True)
    username = models.CharField(max_length=40)  # Добавим unique

    # Обязательные поля для стандартной аутентификации Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Указываем, какой менеджер использовать
    objects = CustomUserManager()

    # Указываем, какое поле будет использоваться для входа (вместо username по умолчанию)
    USERNAME_FIELD = 'login'

    # Поля, которые будут запрашиваться при создании через createsuperuser
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return self.username

    # (Опционально) Добавляем метод для красивого имени
    def get_full_name(self):
        return self.username