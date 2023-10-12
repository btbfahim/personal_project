from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from .serializers import *
from rest_framework.authtoken.models import Token
from .permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from .response_codes import *
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.template.loader import render_to_string
# Login View
@api_view(['POST'])
def user_login(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return create_response(200, "LOGIN_SUCCESS", True, {"token": token.key}, None, None)


        else:
            return create_response(401, ResponseCodes.ERROR, False, {}, "Invalid Credentials", "Authentication failed")
    except Exception as e:
        return create_response(500, ResponseCodes.ERROR, False, {}, "Error", str(e))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.auth:
        request.auth.delete()
        logout(request)
        return create_response(
            200, ResponseCodes.SUCCESS, True, "logged out successfully", None, None)
    else:
        return create_response(
            400, ResponseCodes.ERROR, False, "No active session found")



@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_employee(request):
    try:
        # Extract the required fields from request.data
        username = request.data['username']
        email = request.data.get('email', '')  # Optional field, hence using .get()
        password = request.data['password']
        role = request.data['role']
        name = request.data['name']
        contact_information = request.data['contact_information']
        position = request.data['position']
        department = request.data['department']
        
        # Create a CustomUser instance manually
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            name=name,
            contact_information=contact_information,
            position=position,
            department=department
        )
        email_subject = 'Welcome to Our Company'
        email_message = render_to_string('welcome_email.html', {'username': username})


        send_mail(
            email_subject,
            '',
            'rahim99033@gmail.com',
            [email],
            html_message=email_message  # This includes the HTML message
        )
        serializer = EmployeeProfileSerializer(user)
        return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)
    except Exception as e:
        return create_response(500, ResponseCodes.ERROR, False, {}, "Error", str(e))
    
@api_view(['GET'])
def list_employees(request):
    employees = CustomUser.objects.all()
    serializer = EmployeeProfileSerializer(employees, many=True)
    return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)

# Create a new employee profile
# Retrieve a specific employee profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_employee(request, user_id):
    try:
        employee = CustomUser.objects.get(id=user_id)
        serializer = EmployeeProfileSerializer(employee)
        return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)
    
    except CustomUser.DoesNotExist:
        error_code = "Not Found"
        error = "Employee not found"

        return create_response(404, ResponseCodes.ERROR, False, None, error_code, error)

# Update a specific employee profile
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_employee(request, user_id):
    if request.user.id != user_id:
        raise PermissionDenied("You can only update your own profile.")
        
    try:
        employee = CustomUser.objects.get(id=user_id)
        serializer = EmployeeProfileSerializer(employee, data=request.data, partial=True)  # Note the 'partial=True'
        
        if serializer.is_valid():
            if 'password' and 'username'  in request.data:  # Checking if 'password' is part of the request data
                password = request.data['password']
                employee.set_password(password)
                employee.username = request.data['username']
            employee.save()  # Manually saving the model instance
            return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)
        else:
            error_code = "Validation Error"
            error = serializer.errors
            return create_response(400, ResponseCodes.ERROR, False, None, error_code, error)
            
    except Exception as e:
        return create_response(404, ResponseCodes.ERROR, False, None, "Employee not found", str(e))

# Delete a specific employee profile
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_employee(request, user_id):
    try:
        employee = CustomUser.objects.get(id=user_id)
        employee.delete()
        return create_response(204, ResponseCodes.SUCCESS, True, None, None, None)
    
    except CustomUser.DoesNotExist:
        error_code = "Not Found"
        error = "Employee not found"

        return create_response(404, ResponseCodes.ERROR, False, None, error_code, error)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return create_response(400, ResponseCodes.ERROR, False, None, "Validation Error", "Both old and new password fields are required.")

    if not request.user.check_password(old_password):
        return create_response(400, ResponseCodes.ERROR, False, None, "Wrong password", "Old password is not correct")

    request.user.set_password(new_password)
    request.user.save()

    update_session_auth_hash(request, request.user)

    return create_response(200, ResponseCodes.SUCCESS, True, "Password updated successfully", None, None)

