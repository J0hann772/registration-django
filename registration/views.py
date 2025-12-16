from django.db import IntegrityError
from django.db.models import Q

from .forms import UserRegistrationForm, PasswordResetStubForm  # <--- Лучше перенести это в самый верх файла
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

        login_or_email = request.POST.get('login_or_email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=login_or_email, password=password)

        if user is not None:
            auth_login(request, user)

            # --- ЛОГИКА "ЗАПОМНИТЬ МЕНЯ" ---
            if remember_me:
                request.session.set_expiry(2592000) # 30 дней
            else:
                request.session.set_expiry(0) # До закрытия браузера
            # -------------------------------

            return redirect('main')
        else:
            return render(request, 'registration/login.html', {'error': 'Неверный логин/почта или пароль'})


def registration(request):
    # Если пришли данные (нажали кнопку)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            # 1. Создаем пользователя, но пока не сохраняем в БД окончательно
            user = form.save(commit=False)

            # 2. Сохраняем пароль в переменную, так как после хеширования (set_password)
            # мы не сможем использовать его для функции authenticate
            raw_password = form.cleaned_data['password']
            user.set_password(raw_password)

            # 3. Сохраняем пользователя в БД
            user.save()

            # 4. Аутентифицируем пользователя (это обязательно перед login)
            # Мы передаем user.login, так как это ваше основное поле, и "сырой" пароль
            user = authenticate(request, username=user.login, password=raw_password)

            # 5. Если аутентификация прошла успешно — выполняем вход
            if user is not None:
                auth_login(request, user)
                # ПЕРЕНАПРАВЛЕНИЕ НА ГЛАВНУЮ
                return redirect('main')

    # Если просто открыли страницу (GET)
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/registration.html', {'form': form})

def logout(request):
    auth_logout(request)  # Удаляет сессию пользователя
    return redirect('main')  # Перенаправляем на главную страницу


def password_reset(request):
    """
    Упрощенный сброс пароля (фундамент).
    Позже здесь добавится отправка email.
    """
    if request.method == 'POST':
        form = PasswordResetStubForm(request.POST)
        if form.is_valid():
            login_data = form.cleaned_data['login_or_email']
            new_pass = form.cleaned_data['new_password']

            # Ищем пользователя
            try:
                user = User.objects.get(Q(login=login_data) | Q(email=login_data))

                # Меняем пароль
                user.set_password(new_pass)
                user.save()

                # Перенаправляем на вход с сообщением об успехе (можно добавить message framework позже)
                return redirect('login')

            except User.DoesNotExist:
                form.add_error('login_or_email', 'Пользователь не найден')
    else:
        form = PasswordResetStubForm()

    return render(request, 'registration/password_reset.html', {'form': form})