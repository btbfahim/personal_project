from .models import CustomUser
from rest_framework import serializers
from rest_framework import serializers
from .models import CustomUser  # Import your CustomUser model



class UserLoginSerializer(serializers.Serializer):  # Not linked to the model
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role', 'name',
            'contact_information', 'position', 'department'
        ]
    
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
