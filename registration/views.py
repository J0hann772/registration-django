from django.db import IntegrityError

from .forms import UserRegistrationForm  # <--- Лучше перенести это в самый верх файла
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model

# Получаем вашу кастомную модель User через рекомендованный метод
User = get_user_model()


# Создаем функции представления здесь.

def guest_login(request):
    """Страница ввода имени для гостя"""
    if request.method == 'POST':
        guest_name = request.POST.get('guest_name')
        if guest_name:
            # Сохраняем имя в сессию (это как временная память браузера)
            request.session['guest_name'] = guest_name
            # Перенаправляем на главную
            return redirect('main')

    return render(request, 'registration/guest_login.html')


def index(request, login=None):
    """
    Основная страница.
    Теперь с защитой: пускает только если есть аккаунт ИЛИ имя гостя.
    """
    user = request.user

    # --- ЛОГИКА ПРОВЕРКИ ГОСТЯ ---
    # Если пользователь НЕ вошел в аккаунт И у него НЕТ имени гостя в сессии
    if not user.is_authenticated and 'guest_name' not in request.session:
        # Перенаправляем его на ввод имени
        return redirect('guest_login')
    # -----------------------------

    context = {
        'user_status': 'Гость',  # Значение по умолчанию
        'is_authenticated': user.is_authenticated
    }

    if user.is_authenticated:
        # Если это реальный пользователь - берем его логин
        context['user_status'] = user.login
        # (или user.username, смотря что хотите отображать)
    else:
        # Если это гость - достаем его имя из сессии
        guest_name = request.session.get('guest_name')
        context['user_status'] = f"{guest_name} (Гость)"

    # Если есть аргумент login из URL, он имеет приоритет для отображения (по вашей старой логике)
    if login:
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