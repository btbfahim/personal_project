from django.urls import path
from . import views

urlpatterns = [
    path('create_employee/', views.create_employee, name='create_employee'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('change_password/', views.change_password, name='change_password'),
]