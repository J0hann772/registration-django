from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Повторите пароль')

    class Meta:
        model = User
        fields = ['login', 'email', 'username', 'password']

    # Переопределяем общий метод проверки
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                # Ошибка не привязывается к конкретному полю, она будет в non_field_errors
                raise forms.ValidationError("Пароли не совпадают")

        return cleaned_data

    def clean_email(self):
        # Получаем введенную почту
        email = self.cleaned_data['email']

        # Переводим в нижний регистр (Adwq -> adwq)
        email = email.lower()

        # Проверяем уникальность уже для "маленьких" букв
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Эта почта уже используется")

        return email