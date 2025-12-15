from django.db import IntegrityError

from .forms import UserRegistrationForm  # <--- Лучше перенести это в самый верх файла
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model

# Получаем вашу кастомную модель User через рекомендованный метод
User = get_user_model()


# Создаем функции представления здесь.

def index(request, login=None):
    """
    Основная страница.
    login: опциональный аргумент из URL (если вы используете два маршрута).
    """
    user = request.user

    context = {
        'user_status': 'Гость',
        'is_authenticated': user.is_authenticated
    }

    if user.is_authenticated:
        context['user_status'] = user.login  # Или user.username, если предпочтительнее
    elif login:
        # Это для случая, когда вы перенаправляете на main_login с логином
        context['user_status'] = login

    return render(request, "registration/index.html", context)


def login(request):
    """
    Обрабатывает вход пользователя.
    """
    if request.method == "GET":
        return render(request, "registration/login.html")

    elif request.method == "POST":
        print('произошла отправка данных для входа')

        # Поле, которое может содержать логин или почту
        login_or_email = request.POST.get('login_or_email')
        password = request.POST.get('password')

        # 1. Используем функцию authenticate, которая пройдет по AUTHENTICATION_BACKENDS
        # и использует LoginOrEmailBackend для поиска по логину ИЛИ email.
        user = authenticate(request, username=login_or_email, password=password)

        if user is not None:
            # 2. Если пользователь найден и пароль верен:
            auth_login(request, user)  # Сохраняем сессию пользователя
            print(f'Пользователь {user.get_username()} успешно вошел.')

            # Перенаправляем на главную страницу
            return redirect('main')
        else:
            # 3. Аутентификация не удалась
            return render(request, 'registration/login.html', {'error': 'Неверный логин/почта или пароль'})


def registration(request):
    # Если пришли данные (нажали кнопку)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        # Запуск всех проверок (встроенных, clean_email, clean)
        if form.is_valid():
            # Если это ModelForm, можно сразу сохранять
            # commit=False позволяет изменить объект перед записью в БД
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')

    # Если просто открыли страницу (GET)
    else:
        form = UserRegistrationForm()

    # Если форма не валидна, она вернется в шаблон уже с ошибками внутри
    return render(request, 'registration/registration.html', {'form': form})

def logout(request):
    auth_logout(request)  # Удаляет сессию пользователя
    return redirect('main')  # Перенаправляем на главную страницу