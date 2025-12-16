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


class PasswordResetStubForm(forms.Form):
    login_or_email = forms.CharField(label='Логин или Почта', widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(label='Повторите пароль',
                                       widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data