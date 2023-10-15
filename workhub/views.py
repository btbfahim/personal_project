from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from user.models import CustomUser
from .permissions import IsManagerUser
from user.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from user.response_codes import ResponseCodes, create_response
from rest_framework import status
from decimal import Decimal
from django.db.models import Sum, F
import csv
from django.http import HttpResponse
@api_view(['GET'])
def project_list(request):
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return create_response(status.HTTP_200_OK, ResponseCodes.SUCCESS, True, serializer.data, None, None)

@api_view(['POST', 'PUT'])
@permission_classes([IsManagerUser])
def project_create_or_update(request, project_id=None):
    if request.method == 'POST':
        project_data = request.data
        if 'name' in project_data and 'description' in project_data:
    
            project = Project.objects.create(
                name=project_data['name'],
                description=project_data['description']
            )
            serializer = ProjectSerializer(project)
            return create_response(status.HTTP_201_CREATED, ResponseCodes.SUCCESS, True, serializer.data, None, None)
        return create_response(status.HTTP_400_BAD_REQUEST, ResponseCodes.ERROR, False, None, "INCOMPLETE_DATA", "Incomplete project data.")

    elif request.method == 'PUT':
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return create_response(status.HTTP_404_NOT_FOUND, ResponseCodes.ERROR, False, None, "PROJECT_NOT_FOUND", "Project not found.")

        project_data = request.data
        if 'name' in project_data:
            project.name = project_data['name']
        if 'description' in project_data:
            project.description = project_data['description']

        project.save() 
        serializer = ProjectSerializer(project)
        return create_response(status.HTTP_200_OK, ResponseCodes.SUCCESS, True, serializer.data, None, None)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_retrieve(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return create_response(status.HTTP_404_NOT_FOUND, ResponseCodes.ERROR, False, None, "PROJECT_NOT_FOUND", "Project not found.")
    
    serializer = ProjectSerializer(project)
    return create_response(status.HTTP_200_OK, ResponseCodes.SUCCESS, True, serializer.data, None, None)

@api_view(['DELETE'])
@permission_classes([IsManagerUser])
def project_delete(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return create_response(status.HTTP_404_NOT_FOUND, ResponseCodes.ERROR, False, None, "PROJECT_NOT_FOUND", "Project not found.")

    project.delete()
    return create_response(status.HTTP_204_NO_CONTENT, ResponseCodes.SUCCESS, True, None, None, None)


@api_view(['POST', 'PUT'])
@permission_classes([IsManagerUser])
def create_or_update_task(request, task_id=None):
    if request.method == 'POST':
        task_data = request.data
        assigned_to_id = task_data.get('assigned_to')
        project_id = task_data.get('project')

        if not CustomUser.objects.filter(id=assigned_to_id).exists():
            return create_response(status.HTTP_400_BAD_REQUEST, ResponseCodes.ERROR, False, None, "USER_NOT_FOUND", "assigned_to user does not exist.")

        if not Project.objects.filter(id=project_id).exists():
            return create_response(status.HTTP_400_BAD_REQUEST, ResponseCodes.ERROR, False, None, "PROJECT_NOT_FOUND", "project does not exist.")

        task = Task.objects.create(
            assigned_to_id=assigned_to_id,
            project_id=project_id,
            name=task_data.get('name'),
            description=task_data.get('description'),
            priority=task_data.get('priority', 'medium'),  
            status=task_data.get('status', 'not_started'), 
            start_date=task_data.get('start_date'),
            due_date=task_data.get('due_date'),
           
        )
     
        task_serializer = TaskSerializer(task)
        return create_response(201, ResponseCodes.SUCCESS, True, task_serializer.data, None, None)

    elif request.method == 'PUT':
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return create_response(404, ResponseCodes.ERROR, False, None, "TASK_NOT_FOUND", "Task not found.")

        task_data = request.data
        assigned_to_id = task_data.get('assigned_to')
        project_id = task_data.get('project')

        if assigned_to_id and not CustomUser.objects.filter(id=assigned_to_id).exists():
            return create_response(400, ResponseCodes.ERROR, False, None, "USER_NOT_FOUND", "assigned_to user does not exist.")

        if project_id and not Project.objects.filter(id=project_id).exists():
            return create_response(400, ResponseCodes.ERROR, False, None, "PROJECT_NOT_FOUND", "project does not exist.")

        task.assigned_to_id = assigned_to_id
        task.project_id = project_id
        task.name = task_data.get('name', task.name)  
        task.description = task_data.get('description', task.description)  
        task.priority = task_data.get('priority', task.priority)  
        task.status = task_data.get('status', task.status) 
        task.start_date = task_data.get('start_date', task.start_date) 
        task.due_date = task_data.get('due_date', task.due_date) 
        task.save()
        serializer = TaskSerializer(task)
        return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_retrieve(request, task_id):
    try:
        task = Task.objects.select_related('project').get(id=task_id)
    except Exception as e:
        return create_response(400, ResponseCodes.ERROR, False, None, "TASK_NOT_FOUND", str(e))

    serializer = TaskSerializer(task)
    return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)

@api_view(['DELETE'])
@permission_classes([IsManagerUser])
def task_delete(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Exception as e:
        return create_response(400, ResponseCodes.ERROR, False, None, "TASK_NOT_FOUND", str(e))


    task.delete()
    return create_response(200, ResponseCodes.SUCCESS, True, None, None, None)
    

@api_view(['PUT'])
@permission_classes([IsManagerUser])
def assign_task_to_employee(request, task_id):
    try:
        user_id=request.data.get('user_id')
        task = Task.objects.get(id=task_id)
        user = CustomUser.objects.get(id=user_id)
    except Exception as e:
        return create_response(400, ResponseCodes.ERROR, False, None, str(e), str(e))
    
    task.assigned_to = user
    task.save()
    serializer=TaskSerializer(task)
    return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def employee_performance(request,employee_id):
    try:
        employee = CustomUser.objects.get(id=employee_id)
    except CustomUser.DoesNotExist:
        return None 
     
    projects_worked_on = Project.objects.filter(tasks__assigned_to=employee).distinct()
    project_performance = {}

    for project in projects_worked_on:
        total_tasks_in_project = Task.objects.filter(project=project).count()
        
        total_tasks_completed_by_employee = Task.objects.filter(project=project, assigned_to=employee, status='completed').count()

        if total_tasks_in_project > 0:
            project_performance[project.name] = (total_tasks_completed_by_employee / total_tasks_in_project) * 100
        else:
            project_performance[project.name] = 0

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="performance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Performance Score'])  
    
    for project_name, score in project_performance.items():
        writer.writerow([project_name, score]) 

    return response