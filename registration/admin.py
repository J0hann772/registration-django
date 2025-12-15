from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    # 1. Настраиваем список пользователей (убираем first_name/last_name)
    list_display = ('login', 'email', 'username', 'is_staff', 'is_active')

    # 2. Настраиваем поиск
    search_fields = ('login', 'email', 'username')

    # 3. Настраиваем сортировку
    ordering = ('login',)

    # 4. Настраиваем форму редактирования пользователя (fieldsets)
    # Убираем ссылки на first_name/last_name и добавляем твои поля
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Персональная информация', {'fields': ('username', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    # 5. Настраиваем форму создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'email', 'username', 'password'),  # Поля при создании
        }),
    )


# Регистрируем модель с новыми настройками
admin.site.register(User, CustomUserAdmin)