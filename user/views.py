from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from .serializers import UserLoginSerializer, EmployeeProfileSerializer
from rest_framework.authtoken.models import Token
from .permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from .response_codes import *

# Registration View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

        # Serialize the user data
        serializer = EmployeeProfileSerializer(user)
        return create_response(200, ResponseCodes.SUCCESS, True, serializer.data, None, None)
    except Exception as e:
        return create_response(500, ResponseCodes.ERROR, False, {}, "Error", str(e))


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


