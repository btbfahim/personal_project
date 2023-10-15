from .models import CustomUser
from rest_framework import serializers
from .models import CustomUser 



class UserLoginSerializer(serializers.Serializer): 
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role', 'name',
            'contact_information', 'position', 'department'
        ]
    

