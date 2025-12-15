from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="main"),
    path('u/<str:login>/', views.index, name="main_login"),
    path('account/login/', views.login, name="login"),
    path('account/registration/', views.registration, name="registration"),
]