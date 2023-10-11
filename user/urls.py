from django.urls import path
from . import views

urlpatterns = [
    path('create_employee/', views.create_employee, name='create_employee'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('employees/', views.list_employees, name='list-employees'),
    path('employees/<int:user_id>/', views.retrieve_employee, name='retrieve-employee'),
    path('employees/<int:user_id>/update/', views.update_employee, name='update-employee'),
    path('employees/<int:user_id>/delete/', views.delete_employee, name='delete-employee'),
    path('change_password/', views.change_password, name='change_password'),
]