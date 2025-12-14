from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, get_user_model


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
    """
    Обрабатывает регистрацию нового пользователя.
    """
    if request.method == "GET":
        return render(request, "registration/registration.html")

    elif request.method == "POST":
        login_val = request.POST.get('login')
        email_val = request.POST.get('email')
        password_val = request.POST.get('password')
        username_val = request.POST.get('username')

        # --- Проверки уникальности (для более дружелюбного сообщения) ---
        if User.objects.filter(login=login_val).exists():
            return render(request, 'registration/registration.html', {'error': 'Этот логин уже используется'})
        elif User.objects.filter(email=email_val).exists():
            return render(request, 'registration/registration.html', {'error': 'Эта почта уже используется'})

        # --- Создание пользователя ---
        try:
            # Используем manager.create_user для хеширования пароля и сохранения
            user = User.objects.create_user(
                login=login_val,
                email=email_val,
                password=password_val,
                username=username_val
            )

            # Автоматически входим после регистрации (опционально)
            # user = authenticate(request, username=login_val, password=password_val)
            # if user is not None:
            #     auth_login(request, user)

            print(f'Пользователь {user.login} успешно зарегистрирован.')

            # Успешная регистрация -> перенаправление на страницу входа
            return redirect('login')

        except IntegrityError as e:
            # Ловит ошибки NOT NULL или другие уникальные ограничения
            print(f"Ошибка целостности БД: {e}")
            return render(request, 'registration/registration.html', {'error': 'Произошла ошибка при сохранении данных.'})

        except Exception as e:
            print(f"Общая ошибка при регистрации: {e}")
            return render(request, 'registration/registration.html', {'error': 'Непредвиденная ошибка сервера.'})