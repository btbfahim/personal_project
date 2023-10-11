from rest_framework.decorators import api_view, permission_classes
from .models import *
from .serializers import *
from user.models import CustomUser
from .permissions import IsManagerUser
from rest_framework.permissions import IsAuthenticated
from .response_codes import ResponseCodes, create_response
from rest_framework import status
from decimal import Decimal
from django.db.models import Sum, F
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
            # Create a new project instance using ORM
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
            priority=task_data.get('priority', 'medium'),  # Default to 'medium' if not provided
            status=task_data.get('status', 'not_started'),  # Default to 'not_started' if not provided
            start_date=task_data.get('start_date'),
            due_date=task_data.get('due_date'),
            # Add other task fields here as needed
        )
        # Serialize the task and send it as a response
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
def employee_performance(request, employee_id):
    try:
        employee = CustomUser.objects.get(id=employee_id, role='employee')
    except CustomUser.DoesNotExist:
        return create_response(404, ResponseCodes.ERROR, False, None, "EMPLOYEE_NOT_FOUND", "Employee not found.")

    # Calculate the number of projects worked on by the employee
    projects_worked = Project.objects.filter(tasks__assigned_to=employee).distinct().count()

    # Calculate the number of completed tasks by the employee
    tasks_completed = Task.objects.filter(assigned_to=employee, status='completed').count()

    # Calculate the performance indicator (for example, based on a specific formula)
    performance_indicator = (tasks_completed / max(projects_worked, 1)) * 100

    # Create a response dictionary with the calculated data
    response_data = {
        "employee_name": employee.name,
        "projects_worked": projects_worked,
        "tasks_completed": tasks_completed,
        "performance_indicator": Decimal(performance_indicator).quantize(Decimal("0.00")),
    }

    return create_response(200, ResponseCodes.SUCCESS, True, response_data, None, None)

@api_view(['GET'])
@permission_classes([IsManagerUser])
def employee_performance(request,employee_id):
    try:
        employee = CustomUser.objects.get(id=employee_id)
    except CustomUser.DoesNotExist:
        return None  # Handle the case where the employee does not exist

    # Find the projects the employee has worked on
    projects_worked_on = Project.objects.filter(tasks__assigned_to=employee).distinct()

    # Create a dictionary to store project names as keys and performance scores as values
    project_performance = {}

    for project in projects_worked_on:
        # Calculate the total tasks in the project
        total_tasks_in_project = Task.objects.filter(project=project).count()
        
        # Calculate the total tasks completed by the employee in the project
        total_tasks_completed_by_employee = Task.objects.filter(project=project, assigned_to=employee, status='completed').count()

        # Calculate the performance score for the project
        if total_tasks_in_project > 0:
            project_performance[project.name] = (total_tasks_completed_by_employee / total_tasks_in_project) * 100
        else:
            project_performance[project.name] = 0
    performance_data = [
    {'project_name': project_name, 'performance_score': score}
    for project_name, score in project_performance.items()
    ]

    serializer = ProjectPerformanceSerializer(data=performance_data, many=True)
    serializer.is_valid()  # Check if the data is valid
    serialized_data = serializer.data
    return create_response(200, ResponseCodes.SUCCESS, True, serialized_data, None, None)