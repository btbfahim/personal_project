from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.project_list, name='project-list'),
    path('projects/create/', views.project_create_or_update, name='project-create'),
    path('projects/update/<int:project_id>/', views.project_create_or_update, name='project-update'),
    path('projects/<int:project_id>/', views.project_retrieve, name='project-retrieve'),
    path('projects/delete/<int:project_id>/', views.project_delete, name='project-delete'),

    path('tasks/create/', views.create_or_update_task, name='task-create'),
    path('tasks/update/<int:task_id>/', views.create_or_update_task, name='task-update'),
    path('tasks/<int:task_id>/', views.task_retrieve, name='task-retrieve'),
    path('tasks/delete/<int:task_id>/', views.task_delete, name='task-delete'),
    
    path('tasks/assign/<int:task_id>/', views.assign_task_to_employee, name='assign-task-to-employee'),
]

