
from rest_framework import serializers
from .models import Project,Task  # Import your CustomUser model


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        
class ProjectPerformanceSerializer(serializers.Serializer):
    project_name = serializers.CharField()
    performance_score = serializers.FloatField()