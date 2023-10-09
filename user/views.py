from rest_framework import serializers
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserLoginSerializer
from .models import CustomUser  # If you're creating an Employee profile during registration
from rest_framework.authtoken.models import Token
from .response_codes import *
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash
@api_view(['POST'])
def user_login(request):
    try:
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return create_response(400, ResponseCodes.ERROR, False, {}, "Validation Error", str(serializer.errors))

        username = serializer.data.get('username')
        password = serializer.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return create_response(200, ResponseCodes.SUCCESS, True, token.key)
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
            200, ResponseCodes.SUCCESS, True, "logged out successfully")
    else:
        return create_response(
            400, ResponseCodes.ERROR, False, "No active session found")


@api_view(['POST'])
# @permission_classes([IsAdminUser])
def create_employee(request):
    serializer = EmployeeProfileSerializer(data=request.data)
    if serializer.is_valid():
        # Manually create CustomUser instance
        user = CustomUser.objects.create_user(**serializer.data)
        user.save()
        return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)
    else:
        return create_response(
            400, ResponseCodes.ERROR, False, "can't be created")


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
            
    except CustomUser.DoesNotExist:
        error_code = "Not Found"
        error = "Employee not found"
        return create_response(404, ResponseCodes.ERROR, False, None, error_code, error)

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
    serializer = PasswordChangeSerializer(data=request.data)
    if serializer.is_valid():
        # Check old password
        if not request.user.check_password(serializer.data.get('old_password')):
            return create_response(400, ResponseCodes.ERROR, False, None, "Wrong password", "Old password is not correct")
        
        # set_password hashes the password
        request.user.set_password(serializer.data.get('new_password'))
        request.user.save()

        # Update session hash to prevent session logout after password change
        update_session_auth_hash(request, request.user)

        return create_response(200, ResponseCodes.SUCCESS, True, "Password updated successfully", None, None)
    else:
        return create_response(400, ResponseCodes.ERROR, False, None, "Validation Error", serializer.errors)
